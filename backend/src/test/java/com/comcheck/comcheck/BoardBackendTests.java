package com.comcheck.comcheck;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Proxy;
import java.util.Base64;
import java.util.List;
import java.util.Optional;

import jakarta.persistence.Column;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Lob;
import jakarta.servlet.Filter;
import jakarta.validation.Validation;

import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.boot.MetadataSources;
import org.hibernate.boot.registry.StandardServiceRegistryBuilder;
import org.junit.jupiter.api.Test;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.Query;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockServletContext;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.test.util.ReflectionTestUtils;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.support.AnnotationConfigWebApplicationContext;
import org.springframework.web.servlet.config.annotation.EnableWebMvc;

import com.comcheck.comcheck.config.SecurityConfig;
import com.comcheck.comcheck.domain.board.controller.BoardController;
import com.comcheck.comcheck.domain.board.dto.BoardRequest;
import com.comcheck.comcheck.domain.board.entity.Board;
import com.comcheck.comcheck.domain.board.entity.Category;
import com.comcheck.comcheck.domain.board.repository.BoardRepository;
import com.comcheck.comcheck.domain.board.service.BoardService;
import com.comcheck.comcheck.domain.estimate.entity.Estimate;
import com.comcheck.comcheck.domain.estimate.repository.EstimateRepository;
import com.comcheck.comcheck.domain.estimateitem.entity.EstimateItem;
import com.comcheck.comcheck.domain.part.entity.Part;
import com.comcheck.comcheck.domain.partspec.entity.PartSpec;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;
import com.comcheck.comcheck.domain.user.security.JwtAuthenticationFilter;
import com.comcheck.comcheck.domain.user.service.JwtTokenProvider;
import com.comcheck.comcheck.global.exception.DeletedBoardException;
import com.comcheck.comcheck.global.exception.ForbiddenException;
import com.comcheck.comcheck.global.exception.GlobalExceptionHandler;
import com.comcheck.comcheck.global.exception.NotFoundException;
import com.comcheck.comcheck.global.exception.SecurityErrorResponseWriter;
import com.comcheck.comcheck.global.exception.UnauthorizedException;

// These tests use in-memory repository doubles, never an application datasource.
class BoardBackendTests {
    private static final String BODY =
            "{\"category\":\"FREE\",\"title\":\"Test title\",\"content\":\"Test content\"}";

    @Test
    void quotedColumnsMatchTheSqlScript() throws Exception {
        for (var field : Board.class.getDeclaredFields()) {
            Column column = field.getAnnotation(Column.class);
            if (column != null) {
                assertTrue(column.name().startsWith("\"") && column.name().endsWith("\""));
            }
        }
        assertEquals("\"post_id\"", Board.class.getDeclaredField("boardId")
                .getAnnotation(Column.class).name());
        assertEquals("\"user_id\"", Board.class.getDeclaredField("writer")
                .getAnnotation(JoinColumn.class).name());
        assertNotNull(Board.class.getDeclaredField("content").getAnnotation(Lob.class));
    }

    @Test
    void resolvedStatusIsStoredAndClearedWhenCategoryChanges() {
        Store store = new Store();
        Board board = new Board(store.user, Category.QNA, "Question", "Content");
        board.changeResolved(true);
        assertTrue(board.isResolved());
        board.update(Category.FREE, "Title", "Content");
        assertFalse(board.isResolved());
        assertThrows(IllegalStateException.class, () -> board.changeResolved(true));
    }

    @Test
    void pinnedStatusIsClearedWhenCategoryChanges() {
        Board board = new Board(new Store().user, Category.NOTICE, "Notice", "Content");
        board.changePinned(true);
        assertTrue(board.isPinned());
        board.update(Category.FREE, "Title", "Content");
        assertFalse(board.isPinned());
    }

    @Test
    void ownershipHandlesNullAndOtherUsers() {
        Board board = new Store().board;
        assertTrue(board.isWrittenBy(7L));
        assertFalse(board.isWrittenBy(8L));
        assertFalse(board.isWrittenBy(null));
    }

    @Test
    void creationUsesAuthenticatedUserAndTrimsTitle() {
        Store store = new Store();
        var result = store.service.createBoard(form("  Title  "), 7L);
        assertEquals(7L, result.getWriterId());
        assertEquals("Title", result.getTitle());
        assertEquals("Content", result.getContent());
    }

    @Test
    void creationRejectsMissingOrUnknownUser() {
        Store store = new Store();
        assertThrows(UnauthorizedException.class,
                () -> store.service.createBoard(form("Title"), null));
        assertThrows(UnauthorizedException.class,
                () -> store.service.createBoard(form("Title"), 99L));
    }

    @Test
    void anotherUserCannotUpdateOrDelete() {
        Store store = new Store();
        assertThrows(ForbiddenException.class,
                () -> store.service.updateBoard(42L, form("Changed"), 8L));
        assertThrows(ForbiddenException.class,
                () -> store.service.deleteBoard(42L, 8L));
        assertEquals("Original", store.board.getTitle());
        assertFalse(store.board.isDeleted());
    }

    @Test
    void deletedPostsCannotBeReadUpdatedOrCountedAgain() {
        Store store = new Store();
        store.service.deleteBoard(42L, 7L);
        assertTrue(store.board.isDeleted());
        assertThrows(DeletedBoardException.class, () -> store.service.getBoard(42L));
        assertThrows(DeletedBoardException.class,
                () -> store.service.updateBoard(42L, form("Changed"), 7L));
        assertThrows(DeletedBoardException.class, () -> store.service.increaseView(42L));
    }

    @Test
    void missingPostRaisesNotFound() {
        assertThrows(NotFoundException.class, () -> new Store().service.getBoard(99L));
    }

    @Test
    void listBoundsAndKeywordAreNormalized() {
        Store store = new Store();
        store.service.getBoards(-1, 500, Category.FREE, "  keyword  ");
        assertEquals(0, store.pageable.getPageNumber());
        assertEquals(50, store.pageable.getPageSize());
        assertEquals("keyword", store.keyword);
        store.service.getBoards(0, 0, null, "  ");
        assertEquals(1, store.pageable.getPageSize());
        assertNull(store.keyword);
    }

    @Test
    void titleAndContentLimitsAreValidated() {
        try (var factory = Validation.buildDefaultValidatorFactory()) {
            BoardRequest request = form("x".repeat(101));
            request.setContent("x".repeat(1001));
            var violations = factory.getValidator().validate(request);
            assertTrue(violations.stream().anyMatch(v -> v.getPropertyPath().toString().equals("title")));
            assertTrue(violations.stream().anyMatch(v -> v.getPropertyPath().toString().equals("content")));
        }
    }

    @Test
    void listAndCountQueriesParseWithoutADataSource() throws Exception {
        Query query = BoardRepository.class
                .getMethod("search", Category.class, String.class, Pageable.class)
                .getAnnotation(Query.class);
        assertTrue(query.value().contains("b.isDeleted = false"));
        assertTrue(query.countQuery().contains("b.isDeleted = false"));

        var registry = new StandardServiceRegistryBuilder()
                .applySetting("hibernate.dialect", "org.hibernate.dialect.OracleDialect")
                .applySetting("hibernate.boot.allow_jdbc_metadata_access", false)
                .applySetting("hibernate.hbm2ddl.auto", "none")
                .build();
        try (SessionFactory factory = new MetadataSources(registry)
                .addAnnotatedClass(Board.class).addAnnotatedClass(User.class)
                .buildMetadata().buildSessionFactory();
             Session session = factory.openSession()) {
            session.createSelectionQuery(query.value(), Board.class);
            session.createSelectionQuery(query.countQuery(), Long.class);
        } finally {
            StandardServiceRegistryBuilder.destroy(registry);
        }
    }

    @Test
    void controllerUsesJwtPrincipalRatherThanSession() {
        BoardController controller = new BoardController(new Store().service);
        var authenticated = new UsernamePasswordAuthenticationToken(7L, null, List.of());
        assertEquals(7L, controller.create(form("Title"), authenticated)
                .getBody().getWriterId());
        assertThrows(UnauthorizedException.class, () -> controller.create(form("Title"), null));
        var anonymous = new UsernamePasswordAuthenticationToken("anonymousUser", null, List.of());
        assertThrows(UnauthorizedException.class,
                () -> controller.create(form("Title"), anonymous));
    }

    @Test
    void estimateQueriesAlsoParseWithoutADataSource() {
        var registry = new StandardServiceRegistryBuilder()
                .applySetting("hibernate.dialect", "org.hibernate.dialect.OracleDialect")
                .applySetting("hibernate.boot.allow_jdbc_metadata_access", false)
                .applySetting("hibernate.hbm2ddl.auto", "none")
                .build();
        try (SessionFactory factory = new MetadataSources(registry)
                .addAnnotatedClass(User.class).addAnnotatedClass(Estimate.class)
                .addAnnotatedClass(EstimateItem.class).addAnnotatedClass(Part.class)
                .addAnnotatedClass(PartSpec.class)
                .buildMetadata().buildSessionFactory();
             Session session = factory.openSession()) {
            for (var method : EstimateRepository.class.getMethods()) {
                Query query = method.getAnnotation(Query.class);
                if (query != null) session.createSelectionQuery(query.value(), Object.class);
            }
        } finally {
            StandardServiceRegistryBuilder.destroy(registry);
        }
    }

    @Test
    void securityAllowsPublicReadsButRequiresJwtForWrites() throws Exception {
        try (var context = webContext()) {
            MockMvc mvc = mvc(context);
            mvc.perform(get("/api/boards")).andExpect(status().isOk());
            mvc.perform(get("/api/boards/42")).andExpect(status().isOk());
            mvc.perform(post("/api/boards").contentType(MediaType.APPLICATION_JSON).content(BODY))
                    .andExpect(status().isUnauthorized());
            mvc.perform(put("/api/boards/42").contentType(MediaType.APPLICATION_JSON).content(BODY))
                    .andExpect(status().isUnauthorized());
            mvc.perform(delete("/api/boards/42")).andExpect(status().isUnauthorized());

            var tokens = context.getBean(JwtTokenProvider.class);
            mvc.perform(post("/api/boards").header("Authorization", "Bearer " + tokens.createToken(7L))
                    .contentType(MediaType.APPLICATION_JSON).content(BODY))
                    .andExpect(status().isCreated());
            mvc.perform(put("/api/boards/42").header("Authorization", "Bearer " + tokens.createToken(8L))
                    .contentType(MediaType.APPLICATION_JSON).content(BODY))
                    .andExpect(status().isForbidden());
        }
    }

    @Test
    void developmentCorsAllowsBothLocalhostForms() throws Exception {
        try (var context = webContext()) {
            MockMvc mvc = mvc(context);
            for (String origin : List.of("http://localhost:5173", "http://127.0.0.1:5173")) {
                var response = mvc.perform(options("/api/boards")
                        .header("Origin", origin)
                        .header("Access-Control-Request-Method", "GET")
                        .header("Access-Control-Request-Headers", "Authorization"))
                        .andExpect(status().isOk()).andReturn().getResponse();
                assertEquals(origin, response.getHeader("Access-Control-Allow-Origin"));
            }
        }
    }

    private static BoardRequest form(String title) {
        BoardRequest request = new BoardRequest();
        request.setCategory(Category.FREE);
        request.setTitle(title);
        request.setContent("Content");
        return request;
    }

    private static AnnotationConfigWebApplicationContext webContext() {
        var context = new AnnotationConfigWebApplicationContext();
        context.setServletContext(new MockServletContext());
        context.register(SecurityConfig.class, TestWebConfig.class);
        context.refresh();
        return context;
    }

    private static MockMvc mvc(AnnotationConfigWebApplicationContext context) {
        return MockMvcBuilders.webAppContextSetup(context)
                .addFilters(context.getBean("springSecurityFilterChain", Filter.class)).build();
    }

    @Configuration(proxyBeanMethods = false)
    @EnableWebMvc
    static class TestWebConfig {
        @Bean BoardController controller() { return new BoardController(new Store().service); }
        @Bean GlobalExceptionHandler exceptionHandler() { return new GlobalExceptionHandler(); }
        @Bean SecurityErrorResponseWriter errorWriter() { return new SecurityErrorResponseWriter(); }
        @Bean JwtTokenProvider tokenProvider() {
            return new JwtTokenProvider(Base64.getEncoder().encodeToString(new byte[64]));
        }
        @Bean JwtAuthenticationFilter jwtFilter(JwtTokenProvider provider, SecurityErrorResponseWriter writer) {
            return new JwtAuthenticationFilter(provider, writer);
        }
    }

    // Interface proxies avoid database connections and runtime mocking agents.
    private static <T> T repository(Class<T> type, InvocationHandler handler) {
        return type.cast(Proxy.newProxyInstance(type.getClassLoader(), new Class<?>[] { type }, handler));
    }

    private static class Store {
        final User user = new User("test@example.com", "test-hash", "tester");
        Board board;
        Pageable pageable;
        String keyword;
        final BoardService service;

        Store() {
            ReflectionTestUtils.setField(user, "userId", 7L);
            board = new Board(user, Category.FREE, "Original", "Content");
            ReflectionTestUtils.setField(board, "boardId", 42L);
            BoardRepository posts = repository(BoardRepository.class, (proxy, method, args) -> {
                return switch (method.getName()) {
                    case "findById" -> args[0].equals(42L) ? Optional.of(board) : Optional.empty();
                    case "save" -> {
                        board = (Board) args[0];
                        ReflectionTestUtils.setField(board, "boardId", 42L);
                        yield board;
                    }
                    case "search" -> {
                        pageable = (Pageable) args[2];
                        keyword = (String) args[1];
                        yield new PageImpl<>(List.of(board), pageable, 1);
                    }
                    default -> throw new UnsupportedOperationException(method.getName());
                };
            });
            UserRepository users = repository(UserRepository.class, (proxy, method, args) -> {
                if (method.getName().equals("findById")) {
                    return args[0].equals(7L) ? Optional.of(user) : Optional.empty();
                }
                throw new UnsupportedOperationException(method.getName());
            });
            service = new BoardService(posts, users);
        }
    }
}

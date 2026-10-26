package com.comcheck.comcheck.domain.board.service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import com.comcheck.comcheck.domain.board.dto.BoardCommentRequest;
import com.comcheck.comcheck.domain.board.dto.BoardCommentResponse;
import com.comcheck.comcheck.domain.board.dto.BoardLikeResponse;
import com.comcheck.comcheck.domain.board.dto.BoardDetailResponse;
import com.comcheck.comcheck.domain.board.dto.BoardListResponse;
import com.comcheck.comcheck.domain.board.dto.BoardPageResponse;
import com.comcheck.comcheck.domain.board.dto.BoardRequest;
import com.comcheck.comcheck.domain.board.entity.Board;
import com.comcheck.comcheck.domain.board.entity.BoardComment;
import com.comcheck.comcheck.domain.board.entity.BoardLike;
import com.comcheck.comcheck.domain.board.entity.Category;
import com.comcheck.comcheck.domain.board.repository.BoardRepository;
import com.comcheck.comcheck.domain.board.repository.BoardCommentRepository;
import com.comcheck.comcheck.domain.board.repository.BoardLikeRepository;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;
import com.comcheck.comcheck.global.exception.DeletedBoardException;
import com.comcheck.comcheck.global.exception.ForbiddenException;
import com.comcheck.comcheck.global.exception.NotFoundException;
import com.comcheck.comcheck.global.exception.UnauthorizedException;

@Service
@Transactional(readOnly = true)

public class BoardService {
    

    // 한쪽에 최대 몇 개까지 허용할건지 결정
    private static final int MAX_PAGE_SIZE = 50;
    private static final long MAX_IMAGE_SIZE = 5L * 1024 * 1024;
    private static final Set<String> ALLOWED_IMAGE_TYPES = Set.of(
            "image/jpeg", "image/png", "image/webp", "image/gif");
    private static final Path BOARD_IMAGE_DIRECTORY = Path.of("uploads", "board").toAbsolutePath().normalize();

    // 글 DB
    private final BoardRepository boardRepository;

    // 회원 DB
    private final UserRepository userRepository;
    private final BoardCommentRepository boardCommentRepository;
    private final BoardLikeRepository boardLikeRepository;

    @Autowired
    public BoardService(
            BoardRepository boardRepository,
            UserRepository userRepository,
            BoardCommentRepository boardCommentRepository,
            BoardLikeRepository boardLikeRepository) {
        this.boardRepository = boardRepository;
        this.userRepository = userRepository;
        this.boardCommentRepository = boardCommentRepository;
        this.boardLikeRepository = boardLikeRepository;
    }

    // 기존 단위 테스트와 호환을 위한 생성자다. 실제 Spring 실행에서는 위 생성자가 사용된다.
    public BoardService(BoardRepository boardRepository, UserRepository userRepository) {
        this(boardRepository, userRepository, null, null);
    }

    // 글 목록
    public BoardPageResponse getBoards(int page, int size, Category category, String keyword) {
        // 이상한 값 막기
        int safePage = Math.max(page, 0);
        int safeSize = Math.min(Math.max(size, 1), MAX_PAGE_SIZE);

        // 검색어 정리: 공백뿐인게 있으면 제외
        String safeKeyword = null;
        if (keyword != null && !keyword.isBlank()) {
            safeKeyword = keyword.trim();
        }

        // 페이지 요청서 만들기
        Sort sort = Sort.by(
                Sort.Order.desc("isPinned"),
                Sort.Order.desc("boardId"));
        Pageable pageable = PageRequest.of(safePage, safeSize, sort);

        // 글 목록 조회(작성자도 한번에 조회)
        Page<Board> result = boardRepository.search(category, safeKeyword, pageable);

        // 가져왔으니까 dto 목록으로 하나씩 옮겨 담기
        List<BoardListResponse> boards = new ArrayList<>();
        for (Board board : result.getContent()) {
            boards.add(new BoardListResponse(board));
        }
        return new BoardPageResponse(boards, result);
    }

    // 글 상세
    public BoardDetailResponse getBoard(Long boardId) {
        Board board = findBoard(boardId);
        return new BoardDetailResponse(board);
    }

    // 조회수 증가
    // @Transactional: Spring Boot에서 데이터베이스 작업을 하나의 트랜잭션(Transaction)으로 묶어서 관리하는 어노테이션,
    // DB작업이 모두 성공하면 저장, 못하면 이전 상태로 되돌리기
    @Transactional
    public void increaseView(Long boardId) {

        Board board = findBoard(boardId);
        board.increaseViewCount();
    }

    // 글 작성
    @Transactional
    public BoardDetailResponse createBoard(BoardRequest request, Long loginUserId) {
        return createBoard(request, null, loginUserId);
    }

    @Transactional
    public BoardDetailResponse createBoard(BoardRequest request, MultipartFile image, Long loginUserId) {
        if (loginUserId == null) {
            throw new UnauthorizedException("로그인이 필요합니다.");
        }
        // Resolve the writer from the authenticated JWT user ID.
        User writer = userRepository.findById(loginUserId)
                .orElseThrow(() -> new UnauthorizedException("회원 정보를 찾을 수 없습니다."));

        // 2) 새 글 만들기 (제목은 앞뒤 공백 제거, 내용은 줄바꿈·띄어쓰기를 그대로 보존)
        Board board = new Board(writer, request.getCategory(), request.getTitle().trim(), request.getContent());

        // 3) 저장 (INSERT) → 시퀀스로 받은 글 번호가 들어 있는 객체를 돌려받는다
        Board saved = boardRepository.save(board);

        String imageUrl = storeImage(image);
        if (imageUrl != null) {
            saved.changeImageUrl(imageUrl);
        }

        return new BoardDetailResponse(saved);
    }

    // 글 수정
    @Transactional
    public BoardDetailResponse updateBoard(Long boardId, BoardRequest request, Long loginUserId){
        return updateBoard(boardId, request, null, loginUserId);
    }

    @Transactional
    public BoardDetailResponse updateBoard(
            Long boardId, BoardRequest request, MultipartFile image, Long loginUserId) {
        Board board = findBoard(boardId);
        checkWriter(board, loginUserId);

        board.update(request.getCategory(), request.getTitle().trim(), request.getContent());

        // 새 파일 저장에 성공한 뒤에만 기존 파일을 지워서, 업로드 실패 시 기존 이미지를 보존한다.
        String newImageUrl = storeImage(image);
        if (newImageUrl != null) {
            deleteImage(board.getImageUrl());
            board.changeImageUrl(newImageUrl);
        } else if (request.isRemoveImage()) {
            deleteImage(board.getImageUrl());
            board.changeImageUrl(null);
        }

        return new BoardDetailResponse(board);
    }

    // 글삭제
    @Transactional
    public void deleteBoard(Long boardId, Long loginUserId) {
        Board board = findBoard(boardId);
        checkWriter(board, loginUserId);

        board.delete();
        deleteImage(board.getImageUrl());
    }

    public List<BoardCommentResponse> getComments(Long boardId) {
        findBoard(boardId);
        return commentRepository().findByBoardBoardIdAndIsDeletedFalseOrderByCreatedAtAsc(boardId).stream()
                .map(BoardCommentResponse::new)
                .toList();
    }

    @Transactional
    public BoardCommentResponse createComment(Long boardId, BoardCommentRequest request, Long loginUserId) {
        Board board = findBoard(boardId);
        User writer = findUser(loginUserId);
        BoardComment comment = new BoardComment(board, writer, request.getContent().trim());
        return new BoardCommentResponse(commentRepository().save(comment));
    }

    @Transactional
    public BoardCommentResponse updateComment(
            Long boardId, Long commentId, BoardCommentRequest request, Long loginUserId) {
        BoardComment comment = findComment(boardId, commentId);
        checkCommentWriter(comment, loginUserId);
        comment.update(request.getContent().trim());
        return new BoardCommentResponse(comment);
    }

    @Transactional
    public void deleteComment(Long boardId, Long commentId, Long loginUserId) {
        BoardComment comment = findComment(boardId, commentId);
        checkCommentWriter(comment, loginUserId);
        comment.delete();
    }

    public BoardLikeResponse getLikeStatus(Long boardId, Long loginUserId) {
        findBoard(boardId);
        boolean liked = loginUserId != null
                && likeRepository().existsByBoardBoardIdAndUserUserId(boardId, loginUserId);
        return new BoardLikeResponse(likeRepository().countByBoardBoardId(boardId), liked);
    }

    @Transactional
    public BoardLikeResponse toggleLike(Long boardId, Long loginUserId) {
        Board board = findBoard(boardId);
        User user = findUser(loginUserId);
        BoardLikeRepository repository = likeRepository();
        boolean liked = repository.existsByBoardBoardIdAndUserUserId(boardId, loginUserId);
        if (liked) {
            repository.deleteByBoardBoardIdAndUserUserId(boardId, loginUserId);
        } else {
            repository.save(new BoardLike(board, user));
        }
        return new BoardLikeResponse(repository.countByBoardBoardId(boardId), !liked);
    }

    // 글삭제 안내문구
    private Board findBoard(Long boardId) {
        Board board = boardRepository.findById(boardId)
                .orElseThrow(() -> new NotFoundException("게시글을 찾을 수 없습니다."));
        if (board.isDeleted()) {
            throw new DeletedBoardException("삭제된 게시물입니다.");
        }
        return board;
    }

    private User findUser(Long userId) {
        if (userId == null) {
            throw new UnauthorizedException("로그인이 필요합니다.");
        }
        return userRepository.findById(userId)
                .orElseThrow(() -> new UnauthorizedException("회원 정보를 찾을 수 없습니다."));
    }

    private BoardComment findComment(Long boardId, Long commentId) {
        findBoard(boardId);
        BoardComment comment = commentRepository().findById(commentId)
                .orElseThrow(() -> new NotFoundException("댓글을 찾을 수 없습니다."));
        if (comment.isDeleted() || !boardId.equals(comment.getBoard().getBoardId())) {
            throw new NotFoundException("댓글을 찾을 수 없습니다.");
        }
        return comment;
    }

    // 작성자 본인이 아니면 권한 불충분 - 403 예외 처리
    private void checkWriter(Board board, Long loginUserId) {
        if (!board.isWrittenBy(loginUserId)) {
            throw new ForbiddenException("작성자만 수정하거나 삭제할 수 있습니다.");
        }
    }

    private void checkCommentWriter(BoardComment comment, Long loginUserId) {
        if (!comment.isWrittenBy(loginUserId)) {
            throw new ForbiddenException("댓글 작성자만 수정하거나 삭제할 수 있습니다.");
        }
    }

    private BoardCommentRepository commentRepository() {
        if (boardCommentRepository == null) {
            throw new IllegalStateException("댓글 저장소가 설정되지 않았습니다.");
        }
        return boardCommentRepository;
    }

    private BoardLikeRepository likeRepository() {
        if (boardLikeRepository == null) {
            throw new IllegalStateException("좋아요 저장소가 설정되지 않았습니다.");
        }
        return boardLikeRepository;
    }

    private String storeImage(MultipartFile image) {
        if (image == null || image.isEmpty()) {
            return null;
        }
        if (image.getSize() > MAX_IMAGE_SIZE) {
            throw new IllegalArgumentException("이미지는 5MB 이하만 첨부할 수 있습니다.");
        }
        if (!ALLOWED_IMAGE_TYPES.contains(image.getContentType())) {
            throw new IllegalArgumentException("JPG, PNG, WEBP, GIF 이미지만 첨부할 수 있습니다.");
        }

        try {
            Files.createDirectories(BOARD_IMAGE_DIRECTORY);
            String filename = UUID.randomUUID() + extensionFor(image.getContentType());
            Path destination = BOARD_IMAGE_DIRECTORY.resolve(filename).normalize();
            if (!destination.startsWith(BOARD_IMAGE_DIRECTORY)) {
                throw new IllegalArgumentException("이미지 저장 경로가 올바르지 않습니다.");
            }
            Files.copy(image.getInputStream(), destination, StandardCopyOption.REPLACE_EXISTING);
            return "/uploads/boards/" + filename;
        } catch (IOException exception) {
            throw new IllegalStateException("게시글 이미지를 저장하지 못했습니다.");
        }
    }

    private void deleteImage(String imageUrl) {
        if (imageUrl == null || !imageUrl.startsWith("/uploads/boards/")) {
            return;
        }
        Path target = BOARD_IMAGE_DIRECTORY.resolve(imageUrl.substring("/uploads/boards/".length())).normalize();
        if (!target.startsWith(BOARD_IMAGE_DIRECTORY)) {
            return;
        }
        try {
            Files.deleteIfExists(target);
        } catch (IOException ignored) {
            // 파일 정리 실패는 게시글 DB 작업을 막지 않는다.
        }
    }

    private String extensionFor(String contentType) {
        return switch (contentType) {
            case "image/jpeg" -> ".jpg";
            case "image/png" -> ".png";
            case "image/webp" -> ".webp";
            case "image/gif" -> ".gif";
            default -> throw new IllegalArgumentException("지원하지 않는 이미지 형식입니다.");
        };
    }
}

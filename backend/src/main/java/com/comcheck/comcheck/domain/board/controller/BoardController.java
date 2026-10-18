package com.comcheck.comcheck.domain.board.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.SessionAttribute;

import com.comcheck.comcheck.domain.board.dto.BoardDetailResponse;
import com.comcheck.comcheck.domain.board.dto.BoardPageResponse;
import com.comcheck.comcheck.domain.board.dto.BoardRequest;
import com.comcheck.comcheck.domain.board.entity.Category;
import com.comcheck.comcheck.domain.board.service.BoardService;
import com.comcheck.comcheck.global.exception.UnauthorizedException;

import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;

@RestController
@RequestMapping("/api/boards")
@RequiredArgsConstructor
public class BoardController {
    private final BoardService boardService;

    // 글 목록 - 페이징 · 카테고리 · 검색
    // HTTP GET 요청을 처리하는 메서드를 지정하는 어노테이션, 사용자가 특정 URL로 데이터로 요청했을 때 실행할 메서드를 지정하는 것
    @GetMapping
    public BoardPageResponse list(

            // Spring Boot에서 URL에 전달된 파라미터를 가져오는 어노테이션, 내가 사이트에 적은거를 가져와 java 변수에 저장하게 해주는
            // 기능
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "10") int size,
            @RequestParam(name = "category", required = false) Category category,
            @RequestParam(name = "keyword", required = false) String keyword) {

        return boardService.getBoards(page, size, category, keyword);

    }

    // 글 상세 보기
    // @PathVariable: URL 경로에 포함된 값을 가져와 Java 변수에 저장하는 어노테이션
    @GetMapping("/{boardId}")
    public BoardDetailResponse detail(@PathVariable("boardId") Long boardId) {
        return boardService.getBoard(boardId);
    }

    // 조회수 올리기
    // ResponseEntity<Void>: Spring Boot에서 HTTP응답을 반환하지만, Void로 인해 응답 본문은 보내지 않겠다.
    @PostMapping("/{boardId}/views")
    public ResponseEntity<Void> increaseView(
            @PathVariable("boardId") Long boardId) {

        boardService.increaseView(boardId);
        return ResponseEntity.noContent().build(); // HTTP 상태 코드가 204인 응답 객체를 만드는 것
    }

    // 글 작성
    @PostMapping
    // @Valid: 전달받은 데이터가 유효한지 검사
    // @RequestBody: React가 보낸 JSON 데이터를 Java 객체로 변환
    // @SessionAttribute: 서버의 세션에 미리 저장된 값을 꺼내오는 어노테이션
    public ResponseEntity<BoardDetailResponse> create(@Valid @RequestBody BoardRequest request,
            @SessionAttribute(name = SessionConst.LOGIN_USER_ID, required = false) Long loginUserId) {
        Long userId = requireLogin(loginUserId);
        BoardDetailResponse saved = boardService.createBoard(request, userId);
        return ResponseEntity.status(HttpStatus.CREATED).body(saved);
    }

    // 글 수정
    @PutMapping("/{boardId}")
    public BoardDetailResponse update(
            @PathVariable("boardId") Long boardId,
            @Valid @RequestBody BoardRequest request,
            @SessionAttribute(name = SessionConst.LOGIN_USER_ID, required = false) Long loginUserId) {

        Long userId = requireLogin(loginUserId);
        return boardService.updateBoard(boardId, request, userId);
    }

    // 글 삭제
    @DeleteMapping("/{boardId}")
    public ResponseEntity<Void> delete(
            @PathVariable("boardId") Long boardId,
            @SessionAttribute(name = SessionConst.LOGIN_USER_ID, required = false) Long loginUserId) {
        
        Long userId = requireLogin(loginUserId);
        boardService.deleteBoard(boardId, userId);
        return ResponseEntity.noContent().build();
    }

    // 로그인 검사
    private Long requireLogin(Long loginUserId) {
        if (loginUserId == null) {
            throw new UnauthorizedException("로그인이 필요합니다.");
        }
        return loginUserId;
    }

}

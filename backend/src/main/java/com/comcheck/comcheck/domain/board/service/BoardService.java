package com.comcheck.comcheck.domain.board.service;

import java.util.ArrayList;
import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.comcheck.comcheck.domain.board.dto.BoardDetailResponse;
import com.comcheck.comcheck.domain.board.dto.BoardListResponse;
import com.comcheck.comcheck.domain.board.dto.BoardPageResponse;
import com.comcheck.comcheck.domain.board.dto.BoardRequest;
import com.comcheck.comcheck.domain.board.entity.Board;
import com.comcheck.comcheck.domain.board.entity.Category;
import com.comcheck.comcheck.domain.board.repository.BoardRepository;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.user.repository.UserRepository;
import com.comcheck.comcheck.global.exception.DeletedBoardException;
import com.comcheck.comcheck.global.exception.ForbiddenException;
import com.comcheck.comcheck.global.exception.NotFoundException;
import com.comcheck.comcheck.global.exception.UnauthorizedException;

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)

public class BoardService {
    

    // 한쪽에 최대 몇 개까지 허용할건지 결정
    private static final int MAX_PAGE_SIZE = 50;

    // 글 DB
    private final BoardRepository boardRepository;

    // 회원 DB
    private final UserRepository userRepository;

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
        Pageable pageable = PageRequest.of(safePage, safeSize, Sort.by(Sort.Direction.DESC, "boardId"));

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

        return new BoardDetailResponse(saved);
    }

    // 글 수정
    @Transactional
    public BoardDetailResponse updateBoard(Long boardId, BoardRequest request, Long loginUserId){
        Board board = findBoard(boardId);
        checkWriter(board, loginUserId);

        // 값 바꾸기
        board.update(request.getCategory(), request.getTitle().trim(), request.getContent());

        return new BoardDetailResponse(board);
    }

    // 글삭제
    @Transactional
    public void deleteBoard(Long boardId, Long loginUserId) {
        Board board = findBoard(boardId);
        checkWriter(board, loginUserId);

        board.delete();
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

    // 작성자 본인이 아니면 권한 불충분 - 403 예외 처리
    private void checkWriter(Board board, Long loginUserId) {
        if (!board.isWrittenBy(loginUserId)) {
            throw new ForbiddenException("작성자만 수정하거나 삭제할 수 있습니다.");
        }
    }
}

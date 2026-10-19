package com.comcheck.comcheck.domain.Board.service;


import java.util.ArrayList;
import java.util.List;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.comcheck.comcheck.domain.Board.dto.BoardDetailResponse;
import com.comcheck.comcheck.domain.Board.dto.BoardListResponse;
//import BoardPageResponse
import com.comcheck.comcheck.domain.Board.dto.BoardRequest;
import com.comcheck.comcheck.domain.Board.entity.Board;
import com.comcheck.comcheck.domain.Board.entity.Category;
import com.comcheck.comcheck.domain.user.entity.User;
import com.comcheck.comcheck.domain.Board.entity.ViewLog;
import com.comcheck.comcheck.domain.Board.exception.ForbiddenException;
import com.comcheck.comcheck.domain.Board.exception.NotFoundException;
//import com.gyul.backend.exception.UnauthorizedException;
import com.comcheck.comcheck.domain.Board.repository.BoardRepository;
import com.comcheck.comcheck.domain.user.repository.UserRepository;
//import ViewLogRepository

import lombok.RequiredArgsConstructor;

@Service
@RequiredArgsConstructor
@Transactional(readOnly = true)
public class BoardService {

    private static final int MAX_PAGE_SIZE = 50;
    private final BoardRepository boardRepository;

    private final UserRepository memberRepository;

    private final ViewLogRepository viewLogRepository;

    public BoardPageResponse getBoards(int page, int size, Category category, String keyword) {

        // 이상한 값 막기
        int safePage = Math.max(page, 0);
        int safeSize = Math.min(Math.max(size, 1), MAX_PAGE_SIZE);
        // 검색어 정리
        String safeKeyword = null;
        if (keyword != null && !keyword.isBlank()) {
            safeKeyword = keyword.trim();
        }
        // 페이지 요청서 만들기
        Pageable pageable = PageRequest.of(safePage, safeSize, Sort.by(Sort.Direction.DESC, "boardId"));
        // 조회(11/50)

        //

        // 글 목록 조회
        Page<Board> result = boardRepository.search(category, safeKeyword, pageable);

        List<BoardListResponse> boards = new ArrayList<>();
        for (Board board : result.getContent()) {
            boards.add(new BoardListResponse(board));
        }
        return new BoardPageResponse(boards, result);
    }

    // 글 상세
    public BoardDetailResponse getBoard(Long boardId) {
        Board board = findBoard(boardId);
        return new BoardDetailResponse(board); // 여기서 작성자 정보를 꺼낸다 (트랜잭션 안이라 OK)
    }

    // 글번호 찾기
    private Board findBoard(Long boardId) {
        return boardRepository.findById(boardId)
                .orElseThrow(() -> new NotFoundException("게시글을 찾을 수 없습니다."));
    }

    private void checkWriter(Board board, Long loginMemberId) {
        if (!board.isWrittenBy(loginMemberId)) {
            throw new ForbiddenException("작성자만 수정하거나 삭제할 수 있습니다.");
        }
    }

    @Transactional
    public BoardDetailResponse createBoard(BoardRequest request, Long loginMemberId) {

        // 1) 작성자(로그인 회원) 찾기 : 세션에는 번호만 있으므로 DB에서 회원을 꺼낸다
        User writer = UserRepository.findById(userId)
                .orElseThrow(() -> new UnauthorizedException("회원 정보를 찾을 수 없습니다. 다시 로그인해 주세요."));

        // 2) 새 글 만들기 (제목은 앞뒤 공백 제거, 내용은 줄바꿈·띄어쓰기를 그대로 보존)
        Board board = new Board(writer, request.getCategory(), request.getTitle().trim(), request.getContent());

        // 3) 저장 (INSERT) → 시퀀스로 받은 글 번호가 들어 있는 객체를 돌려받는다
        Board saved = boardRepository.save(board);

        return new BoardDetailResponse(saved);
    }

    @Transactional
    public BoardDetailResponse updateBoard(Long boardId, BoardRequest request, Long loginMemberId) {

        Board board = findBoard(boardId); // 1) 글 찾기 (없으면 404)
        checkWriter(board, loginMemberId); // 2) 작성자 확인 (다르면 403)

        // 3) 값 바꾸기 → 트랜잭션 끝에 UPDATE 자동 실행
        board.update(request.getCategory(), request.getTitle().trim(), request.getContent());

        return new BoardDetailResponse(board); // 바뀐 값으로 응답
    }

    @Transactional
    public void deleteBoard(Long boardId, Long memberId) {
        Board board = findBoard(boardId);
        checkWriter(board, memberId);
        boardRepository.delete(board);
    }

    @Transactional
    public void increaseView(Long boardId, Long loginMemberId) {

        Board board = findBoard(boardId); // 1) 글 찾기 (없으면 404)
        board.increaseViewCount(); // 2) 조회수 +1 (변경 감지로 UPDATE)

        // 3) 방명록에 한 줄 쓰기 (INSERT) - 날씨·기온은 06챕터에서 추가
        viewLogRepository.save(new ViewLog(board.getBoardId(), loginMemberId, board.getCategory()));
    }
}

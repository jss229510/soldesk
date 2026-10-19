package com.comcheck.comcheck.domain.board.entity;

import java.time.LocalDateTime;

import org.hibernate.type.YesNoConverter;

import com.comcheck.comcheck.domain.user.entity.User;

import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "BOARD_POSTS")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class Board {
    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "board_seq_generator")
    @SequenceGenerator(name = "board_seq_generator", sequenceName = "SEQ_BOARD_POSTS", allocationSize = 1)

    @Column(name = "post_id")
    private Long boardId; // 글번호

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User writer;

    @Enumerated(EnumType.STRING)
    @Column(name = "board_type")
    private Category category;

    @Column(name = "title")
    private String title;

    @Column(name = "content")
    private String content;

    @Column(name = "view_count")
    private long viewCount;

    // 공지용
    @Convert(converter = YesNoConverter.class)
    @Column(name = "is_pinned", nullable = false)
    private boolean isPinned;

    @Convert(converter = YesNoConverter.class)
    @Column(name = "is_deleted", nullable = false)
    private boolean isDeleted;

    // Q&N용
    @Convert(converter = YesNoConverter.class)
    @Column(name = "is_resolved", nullable = false)
    private boolean isResolved;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    public Board(User writer, Category category, String title, String content) {
        this.writer = writer;
        this.category = category;
        this.title = title;
        this.content = content;
        this.viewCount = 0;
        this.isPinned = false;
        this.isDeleted = false;
        this.isResolved = false;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }

    public void update(Category category, String title, String content) {
        this.category = category;
        this.title = title;
        this.content = content;
        this.updatedAt = LocalDateTime.now();
    }

    public void increaseViewCount() {
        this.viewCount = this.viewCount + 1;
    }

    public boolean isWritterBy(Long userid) {
        return writer.getUserId().equals(userid);
    }

    // 삭제 메서드
    public void delete() {
        this.isDeleted = true;
        this.updatedAt = LocalDateTime.now();
    }

    // 공지사항 상단 고정/해제
    public void changePinned(boolean pinned) {
        if (this.category != Category.NOTICE) {
            throw new IllegalStateException("공지사항만 고정할 수 있습니다.");
        }
        this.isPinned = pinned;
        this.updatedAt = LocalDateTime.now();
    }

    public void changeResolved(boolean resolved) {
        if (this.category != Category.QNA) {
            throw new IllegalStateException("Q&N 게시글만 해결 상태를 변경할 수 있습니다.");
        }
    }
}

package com.comcheck.comcheck.domain.board.entity;

import java.time.LocalDateTime;

import org.hibernate.type.YesNoConverter;

import com.comcheck.comcheck.domain.user.entity.User;

import jakarta.persistence.Column;
import jakarta.persistence.Convert;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Lob;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.SequenceGenerator;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "BOARD_COMMENTS")
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class BoardComment {

    @Id
    @GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "boardCommentSequence")
    @SequenceGenerator(name = "boardCommentSequence", sequenceName = "SEQ_BOARD_COMMENTS", allocationSize = 1)
    @Column(name = "\"comment_id\"")
    private Long commentId;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"post_id\"", nullable = false)
    private Board board;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"user_id\"", nullable = false)
    private User writer;

    @Lob
    @Column(name = "\"content\"", nullable = false)
    private String content;

    @Convert(converter = YesNoConverter.class)
    @Column(name = "\"is_deleted\"", nullable = false)
    private boolean isDeleted;

    @Column(name = "\"created_at\"", nullable = false)
    private LocalDateTime createdAt;

    @Column(name = "\"updated_at\"", nullable = false)
    private LocalDateTime updatedAt;

    public BoardComment(Board board, User writer, String content) {
        this.board = board;
        this.writer = writer;
        this.content = content;
        this.isDeleted = false;
        this.createdAt = LocalDateTime.now();
        this.updatedAt = this.createdAt;
    }

    public void update(String content) {
        this.content = content;
        this.updatedAt = LocalDateTime.now();
    }

    public void delete() {
        this.isDeleted = true;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean isWrittenBy(Long userId) {
        return userId != null && writer != null && userId.equals(writer.getUserId());
    }
}

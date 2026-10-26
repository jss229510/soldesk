package com.comcheck.comcheck.domain.board.entity;

import java.io.Serializable;
import java.time.LocalDateTime;
import java.util.Objects;

import com.comcheck.comcheck.domain.user.entity.User;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.Id;
import jakarta.persistence.IdClass;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import lombok.AccessLevel;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "BOARD_LIKES")
@IdClass(BoardLike.BoardLikeId.class)
@Getter
@NoArgsConstructor(access = AccessLevel.PROTECTED)
public class BoardLike {

    @Id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"post_id\"", nullable = false)
    private Board board;

    @Id
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "\"user_id\"", nullable = false)
    private User user;

    @Column(name = "\"created_at\"", nullable = false)
    private LocalDateTime createdAt;

    public BoardLike(Board board, User user) {
        this.board = board;
        this.user = user;
        this.createdAt = LocalDateTime.now();
    }

    public static class BoardLikeId implements Serializable {
        private Long board;
        private Long user;

        public BoardLikeId() {
        }

        @Override
        public boolean equals(Object object) {
            if (this == object) return true;
            if (!(object instanceof BoardLikeId other)) return false;
            return Objects.equals(board, other.board) && Objects.equals(user, other.user);
        }

        @Override
        public int hashCode() {
            return Objects.hash(board, user);
        }
    }
}

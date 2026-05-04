package com.petiopenal.model;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

public class VirtualCard {

    private Long id;
    private String cardNumber;
    private String holderName;
    private String cvv;
    private LocalDate expirationDate;
    private BigDecimal limit;
    private BigDecimal balance;
    private CardStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public enum CardStatus {
        ACTIVE, INACTIVE, BLOCKED, CANCELLED
    }

    public VirtualCard() {}

    public VirtualCard(Long id, String cardNumber, String holderName, String cvv,
                       LocalDate expirationDate, BigDecimal limit, BigDecimal balance,
                       CardStatus status, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.cardNumber = cardNumber;
        this.holderName = holderName;
        this.cvv = cvv;
        this.expirationDate = expirationDate;
        this.limit = limit;
        this.balance = balance;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getCardNumber() { return cardNumber; }
    public void setCardNumber(String cardNumber) { this.cardNumber = cardNumber; }

    public String getHolderName() { return holderName; }
    public void setHolderName(String holderName) { this.holderName = holderName; }

    public String getCvv() { return cvv; }
    public void setCvv(String cvv) { this.cvv = cvv; }

    public LocalDate getExpirationDate() { return expirationDate; }
    public void setExpirationDate(LocalDate expirationDate) { this.expirationDate = expirationDate; }

    public BigDecimal getLimit() { return limit; }
    public void setLimit(BigDecimal limit) { this.limit = limit; }

    public BigDecimal getBalance() { return balance; }
    public void setBalance(BigDecimal balance) { this.balance = balance; }

    public CardStatus getStatus() { return status; }
    public void setStatus(CardStatus status) { this.status = status; }

    public LocalDateTime getCreatedAt() { return createdAt; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }

    public LocalDateTime getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}

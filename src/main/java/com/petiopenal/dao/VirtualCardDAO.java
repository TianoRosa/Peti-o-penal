package com.petiopenal.dao;

import com.petiopenal.model.VirtualCard;

import java.util.List;
import java.util.Optional;

public interface VirtualCardDAO {

    VirtualCard save(VirtualCard card);

    Optional<VirtualCard> findById(Long id);

    Optional<VirtualCard> findByCardNumber(String cardNumber);

    List<VirtualCard> findByHolderName(String holderName);

    List<VirtualCard> findAll();

    List<VirtualCard> findByStatus(VirtualCard.CardStatus status);

    VirtualCard update(VirtualCard card);

    void deleteById(Long id);

    boolean existsById(Long id);
}

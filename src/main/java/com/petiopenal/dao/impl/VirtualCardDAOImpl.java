package com.petiopenal.dao.impl;

import com.petiopenal.dao.VirtualCardDAO;
import com.petiopenal.model.VirtualCard;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class VirtualCardDAOImpl implements VirtualCardDAO {

    private final Connection connection;

    public VirtualCardDAOImpl(Connection connection) {
        this.connection = connection;
    }

    @Override
    public VirtualCard save(VirtualCard card) {
        String sql = "INSERT INTO virtual_cards (card_number, holder_name, cvv, expiration_date, " +
                     "`limit`, balance, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";
        try (PreparedStatement stmt = connection.prepareStatement(sql, Statement.RETURN_GENERATED_KEYS)) {
            bindCardParams(stmt, card);
            stmt.executeUpdate();
            ResultSet keys = stmt.getGeneratedKeys();
            if (keys.next()) {
                card.setId(keys.getLong(1));
            }
            return card;
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao salvar cartão virtual", e);
        }
    }

    @Override
    public Optional<VirtualCard> findById(Long id) {
        String sql = "SELECT * FROM virtual_cards WHERE id = ?";
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.setLong(1, id);
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                return Optional.of(mapRow(rs));
            }
            return Optional.empty();
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao buscar cartão por ID", e);
        }
    }

    @Override
    public Optional<VirtualCard> findByCardNumber(String cardNumber) {
        String sql = "SELECT * FROM virtual_cards WHERE card_number = ?";
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.setString(1, cardNumber);
            ResultSet rs = stmt.executeQuery();
            if (rs.next()) {
                return Optional.of(mapRow(rs));
            }
            return Optional.empty();
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao buscar cartão por número", e);
        }
    }

    @Override
    public List<VirtualCard> findByHolderName(String holderName) {
        String sql = "SELECT * FROM virtual_cards WHERE holder_name = ?";
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.setString(1, holderName);
            return fetchList(stmt);
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao buscar cartões por titular", e);
        }
    }

    @Override
    public List<VirtualCard> findAll() {
        String sql = "SELECT * FROM virtual_cards";
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            return fetchList(stmt);
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao listar cartões virtuais", e);
        }
    }

    @Override
    public List<VirtualCard> findByStatus(VirtualCard.CardStatus status) {
        String sql = "SELECT * FROM virtual_cards WHERE status = ?";
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.setString(1, status.name());
            return fetchList(stmt);
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao buscar cartões por status", e);
        }
    }

    @Override
    public VirtualCard update(VirtualCard card) {
        String sql = "UPDATE virtual_cards SET card_number = ?, holder_name = ?, cvv = ?, " +
                     "expiration_date = ?, `limit` = ?, balance = ?, status = ?, " +
                     "created_at = ?, updated_at = ? WHERE id = ?";
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            bindCardParams(stmt, card);
            stmt.setLong(10, card.getId());
            stmt.executeUpdate();
            return card;
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao atualizar cartão virtual", e);
        }
    }

    @Override
    public void deleteById(Long id) {
        String sql = "DELETE FROM virtual_cards WHERE id = ?";
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.setLong(1, id);
            stmt.executeUpdate();
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao excluir cartão virtual", e);
        }
    }

    @Override
    public boolean existsById(Long id) {
        String sql = "SELECT 1 FROM virtual_cards WHERE id = ?";
        try (PreparedStatement stmt = connection.prepareStatement(sql)) {
            stmt.setLong(1, id);
            ResultSet rs = stmt.executeQuery();
            return rs.next();
        } catch (SQLException e) {
            throw new RuntimeException("Erro ao verificar existência do cartão", e);
        }
    }

    private void bindCardParams(PreparedStatement stmt, VirtualCard card) throws SQLException {
        stmt.setString(1, card.getCardNumber());
        stmt.setString(2, card.getHolderName());
        stmt.setString(3, card.getCvv());
        stmt.setDate(4, Date.valueOf(card.getExpirationDate()));
        stmt.setBigDecimal(5, card.getLimit());
        stmt.setBigDecimal(6, card.getBalance());
        stmt.setString(7, card.getStatus().name());
        stmt.setTimestamp(8, Timestamp.valueOf(card.getCreatedAt()));
        stmt.setTimestamp(9, Timestamp.valueOf(card.getUpdatedAt()));
    }

    private List<VirtualCard> fetchList(PreparedStatement stmt) throws SQLException {
        List<VirtualCard> cards = new ArrayList<>();
        ResultSet rs = stmt.executeQuery();
        while (rs.next()) {
            cards.add(mapRow(rs));
        }
        return cards;
    }

    private VirtualCard mapRow(ResultSet rs) throws SQLException {
        VirtualCard card = new VirtualCard();
        card.setId(rs.getLong("id"));
        card.setCardNumber(rs.getString("card_number"));
        card.setHolderName(rs.getString("holder_name"));
        card.setCvv(rs.getString("cvv"));
        card.setExpirationDate(rs.getDate("expiration_date").toLocalDate());
        card.setLimit(rs.getBigDecimal("limit"));
        card.setBalance(rs.getBigDecimal("balance"));
        card.setStatus(VirtualCard.CardStatus.valueOf(rs.getString("status")));
        card.setCreatedAt(rs.getTimestamp("created_at").toLocalDateTime());
        card.setUpdatedAt(rs.getTimestamp("updated_at").toLocalDateTime());
        return card;
    }
}

package com.example.order;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

public class OrderProcessor {

    private List<Order> pendingOrders = new ArrayList<>();
    private ExecutorService executor = Executors.newCachedThreadPool();
    private volatile boolean processing = false;

    public void addOrder(Order order) {
        pendingOrders.add(order);
    }

    public void processAllOrders() {
        processing = true;
        for (Order order : pendingOrders) {
            executor.submit(() -> {
                try {
                    processOrder(order);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
            });
        }
        pendingOrders.clear();
        processing = false;
    }

    private void processOrder(Order order) throws Exception {
        // Validate
        if (order == null) return;
        if (order.getItems() == null) return;
        if (order.getItems().size() == 0) return;

        double total = 0;
        for (int i = 0; i < order.getItems().size(); i++) {
            OrderItem item = order.getItems().get(i);
            double itemTotal = item.getPrice() * item.getQuantity();

            // Apply discount
            if (item.getQuantity() > 10) {
                itemTotal = itemTotal * 0.9;
            } else if (item.getQuantity() > 5) {
                itemTotal = itemTotal * 0.95;
            }

            total = total + itemTotal;
        }

        // Apply tax
        double tax = total * 0.08;
        total = total + tax;

        // Round to 2 decimal places
        total = Math.round(total * 100) / 100;

        order.setTotal(total);
        order.setStatus("PROCESSED");

        // Save to database
        saveOrder(order);
    }

    private void saveOrder(Order order) throws Exception {
        java.sql.Connection conn = java.sql.DriverManager.getConnection(
            "jdbc:mysql://localhost/mydb", "root", "password123");
        java.sql.PreparedStatement ps = conn.prepareStatement(
            "UPDATE orders SET total = ?, status = ? WHERE id = ?");
        ps.setDouble(1, order.getTotal());
        ps.setString(2, order.getStatus());
        ps.setLong(3, order.getId());
        ps.executeUpdate();
    }

    public Map<String, List<Order>> groupOrdersByStatus() {
        Map<String, List<Order>> grouped = new HashMap<>();
        for (Order order : pendingOrders) {
            String status = order.getStatus();
            if (!grouped.containsKey(status)) {
                grouped.put(status, new ArrayList<>());
            }
            grouped.get(status).add(order);
        }
        return grouped;
    }

    public List<Order> findExpensiveOrders(double threshold) {
        return pendingOrders.stream()
            .parallel()
            .filter(o -> o.getTotal() > threshold)
            .collect(Collectors.toList());
    }

    public double calculateAverageOrderValue() {
        double sum = 0;
        int count = 0;
        for (Order o : pendingOrders) {
            sum += o.getTotal();
            count++;
        }
        return sum / count;
    }
}

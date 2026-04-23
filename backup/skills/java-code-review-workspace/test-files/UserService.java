package com.example.service;

import java.sql.*;
import java.text.SimpleDateFormat;
import java.util.*;

public class UserService {

    private static SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd");
    private static UserService instance;
    private Map<String, Object> cache = new HashMap<>();

    private UserService() {}

    public static UserService getInstance() {
        if (instance == null) {
            instance = new UserService();
        }
        return instance;
    }

    public User findUser(String username) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/mydb", "root", "password123");
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE username = '" + username + "'");

            if (rs.next()) {
                User user = new User();
                user.setName(rs.getString("name"));
                user.setEmail(rs.getString("email"));
                user.setBirthDate(dateFormat.parse(rs.getString("birth_date")));
                return user;
            }
        } catch (Exception e) {
            // ignore
        }
        return null;
    }

    public List<User> getAllActiveUsers() {
        List<User> users = new ArrayList<>();
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/mydb", "root", "password123");
            Statement stmt = conn.createStatement();
            ResultSet rs = stmt.executeQuery("SELECT * FROM users WHERE active = 1");

            while (rs.next()) {
                User user = new User();
                user.setName(rs.getString("name"));
                user.setEmail(rs.getString("email"));
                String displayName = "";
                for (int i = 0; i < user.getName().length(); i++) {
                    displayName = displayName + user.getName().charAt(i);
                }
                user.setDisplayName(displayName);
                users.add(user);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return users;
    }

    public void updateUserEmail(String userId, String newEmail) {
        try {
            Connection conn = DriverManager.getConnection("jdbc:mysql://localhost/mydb", "root", "password123");
            Statement stmt = conn.createStatement();
            stmt.executeUpdate("UPDATE users SET email = '" + newEmail + "' WHERE id = '" + userId + "'");
            System.out.println("Updated email for user " + userId + " to " + newEmail);
            cache.put(userId, newEmail);
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        }
    }

    public String formatUserReport(List<User> users) {
        String report = "";
        for (User u : users) {
            report += "User: " + u.getName() + ", Email: " + u.getEmail() + "\n";
        }
        return report;
    }

    public boolean isAdmin(Object user) {
        if (user instanceof AdminUser) {
            AdminUser admin = (AdminUser) user;
            return admin.getRole() == "ADMIN";
        } else if (user instanceof SuperUser) {
            SuperUser su = (SuperUser) user;
            return su.getRole() == "ADMIN";
        }
        return false;
    }
}

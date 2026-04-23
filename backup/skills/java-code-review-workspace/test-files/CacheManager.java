package com.example.cache;

import java.lang.reflect.*;
import java.util.*;
import java.util.concurrent.*;

public class CacheManager<K, V> {

    private Map<K, V> cache = new HashMap<>();
    private Map<K, Long> expiryTimes = new HashMap<>();
    private long defaultTtlMs = 60000;
    private static final CacheManager INSTANCE = new CacheManager();

    @SuppressWarnings("unchecked")
    public static <K, V> CacheManager<K, V> getInstance() {
        return INSTANCE;
    }

    public void put(K key, V value) {
        cache.put(key, value);
        expiryTimes.put(key, System.currentTimeMillis() + defaultTtlMs);
    }

    public void put(K key, V value, long ttlMs) {
        cache.put(key, value);
        expiryTimes.put(key, System.currentTimeMillis() + ttlMs);
    }

    public V get(K key) {
        Long expiry = expiryTimes.get(key);
        if (expiry != null && System.currentTimeMillis() > expiry) {
            cache.remove(key);
            expiryTimes.remove(key);
            return null;
        }
        return cache.get(key);
    }

    public void evictExpired() {
        for (K key : cache.keySet()) {
            Long expiry = expiryTimes.get(key);
            if (expiry != null && System.currentTimeMillis() > expiry) {
                cache.remove(key);
                expiryTimes.remove(key);
            }
        }
    }

    public int size() {
        return cache.size();
    }

    public void clear() {
        cache.clear();
        expiryTimes.clear();
    }

    public Map<K, V> getAll() {
        return cache;
    }

    public boolean containsKey(K key) {
        return cache.containsKey(key);
    }

    public V getOrDefault(K key, V defaultValue) {
        if (containsKey(key)) {
            V value = get(key);
            if (value != null) {
                return value;
            }
        }
        return defaultValue;
    }

    // Load cache from any object using reflection
    public void loadFromObject(Object source) {
        try {
            Class<?> clazz = source.getClass();
            Field[] fields = clazz.getDeclaredFields();
            for (Field field : fields) {
                field.setAccessible(true);
                Object value = field.get(source);
                if (value != null) {
                    cache.put((K) field.getName(), (V) value);
                    expiryTimes.put((K) field.getName(), System.currentTimeMillis() + defaultTtlMs);
                }
            }
        } catch (Exception e) {
            // reflection failed, just skip
        }
    }

    public String generateReport() {
        String report = "Cache Report\n";
        report += "============\n";
        report += "Size: " + cache.size() + "\n";
        report += "Entries:\n";
        for (Map.Entry<K, V> entry : cache.entrySet()) {
            report += "  " + entry.getKey() + " => " + entry.getValue() + "\n";
        }
        return report;
    }

    public void copyTo(CacheManager<K, V> other) {
        for (Map.Entry<K, V> entry : cache.entrySet()) {
            other.put(entry.getKey(), entry.getValue());
        }
    }
}

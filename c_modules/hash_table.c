/*
 * hash_table.c — Hash table implementation (separate chaining)
 * Student Record Management System
 */

#include "hash_table.h"
#include <stdio.h>
#include <stdlib.h>

/* ── hash function (integer key) ────────────────────────────────────────── */
static int hash(int key, int capacity) {
    /* Knuth multiplicative hashing */
    unsigned int k = (unsigned int)key;
    return (int)((k * 2654435761u) % (unsigned int)capacity);
}

/* ── create ─────────────────────────────────────────────────────────────── */
HashTable *ht_create(int capacity) {
    if (capacity <= 0) capacity = HT_DEFAULT_SIZE;
    HashTable *ht = (HashTable *)malloc(sizeof(HashTable));
    if (!ht) return NULL;
    ht->buckets  = (HTNode **)calloc(capacity, sizeof(HTNode *));
    if (!ht->buckets) { free(ht); return NULL; }
    ht->capacity = capacity;
    ht->size     = 0;
    return ht;
}

/* ── insert ─────────────────────────────────────────────────────────────── */
int ht_insert(HashTable *ht, const Student *s) {
    int idx = hash(s->student_id, ht->capacity);

    /* check for duplicate */
    HTNode *cur = ht->buckets[idx];
    while (cur) {
        if (cur->data.student_id == s->student_id) {
            fprintf(stderr, "[HT] Duplicate student_id %d — skipped\n", s->student_id);
            return -1;
        }
        cur = cur->next;
    }

    HTNode *node = (HTNode *)malloc(sizeof(HTNode));
    if (!node) return -1;
    student_copy(&node->data, s);
    node->next         = ht->buckets[idx];
    ht->buckets[idx]   = node;
    ht->size++;
    return 0;
}

/* ── search ─────────────────────────────────────────────────────────────── */
Student *ht_search(const HashTable *ht, int id) {
    int idx = hash(id, ht->capacity);
    HTNode *cur = ht->buckets[idx];
    while (cur) {
        if (cur->data.student_id == id) return &cur->data;
        cur = cur->next;
    }
    return NULL;
}

/* ── delete ─────────────────────────────────────────────────────────────── */
int ht_delete(HashTable *ht, int id) {
    int     idx  = hash(id, ht->capacity);
    HTNode *cur  = ht->buckets[idx];
    HTNode *prev = NULL;

    while (cur) {
        if (cur->data.student_id == id) {
            if (prev) prev->next      = cur->next;
            else      ht->buckets[idx] = cur->next;
            free(cur);
            ht->size--;
            return 0;
        }
        prev = cur;
        cur  = cur->next;
    }
    return -1;   /* not found */
}

/* ── update (in-place) ───────────────────────────────────────────────────── */
int ht_update(HashTable *ht, const Student *s) {
    Student *existing = ht_search(ht, s->student_id);
    if (!existing) return -1;
    student_copy(existing, s);
    return 0;
}

/* ── print all buckets ───────────────────────────────────────────────────── */
void ht_print(const HashTable *ht) {
    printf("\n=== Hash Table (size=%d, capacity=%d, load=%.2f) ===\n",
           ht->size, ht->capacity, ht_load_factor(ht));
    for (int i = 0; i < ht->capacity; i++) {
        if (!ht->buckets[i]) continue;
        printf("  Bucket[%3d]: ", i);
        HTNode *cur = ht->buckets[i];
        while (cur) {
            printf("[%d:%s %s] ", cur->data.student_id,
                   cur->data.first_name, cur->data.last_name);
            cur = cur->next;
        }
        printf("\n");
    }
}

/* ── load factor ─────────────────────────────────────────────────────────── */
float ht_load_factor(const HashTable *ht) {
    return (float)ht->size / (float)ht->capacity;
}

int ht_size(const HashTable *ht) { return ht->size; }

/* ── dump to flat array ──────────────────────────────────────────────────── */
int ht_to_array(const HashTable *ht, Student *arr, int capacity) {
    int count = 0;
    for (int i = 0; i < ht->capacity && count < capacity; i++) {
        HTNode *cur = ht->buckets[i];
        while (cur && count < capacity) {
            student_copy(&arr[count++], &cur->data);
            cur = cur->next;
        }
    }
    return count;
}

/* ── destroy ─────────────────────────────────────────────────────────────── */
void ht_destroy(HashTable *ht) {
    for (int i = 0; i < ht->capacity; i++) {
        HTNode *cur = ht->buckets[i];
        while (cur) {
            HTNode *next = cur->next;
            free(cur);
            cur = next;
        }
    }
    free(ht->buckets);
    free(ht);
}

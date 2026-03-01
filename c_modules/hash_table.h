/*
 * hash_table.h — Hash table keyed on student_id (chaining for collisions)
 * Student Record Management System
 */

#ifndef HASH_TABLE_H
#define HASH_TABLE_H

#include "student.h"

#define HT_DEFAULT_SIZE  101   /* prime for better distribution */

/* ─── Chain node ─────────────────────────────────────────────────────────── */
typedef struct HTNode {
    Student       data;
    struct HTNode *next;
} HTNode;

/* ─── Table ──────────────────────────────────────────────────────────────── */
typedef struct {
    HTNode **buckets;
    int      capacity;
    int      size;
} HashTable;

/* ─── API ────────────────────────────────────────────────────────────────── */
HashTable *ht_create(int capacity);
void       ht_destroy(HashTable *ht);

int        ht_insert(HashTable *ht, const Student *s);
Student   *ht_search(const HashTable *ht, int id);
int        ht_delete(HashTable *ht, int id);
int        ht_update(HashTable *ht, const Student *s);

void       ht_print(const HashTable *ht);
float      ht_load_factor(const HashTable *ht);
int        ht_size(const HashTable *ht);

/* Dump all entries into a flat array (caller allocates) */
int        ht_to_array(const HashTable *ht, Student *arr, int capacity);

#endif /* HASH_TABLE_H */

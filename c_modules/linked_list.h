/*
 * linked_list.h — Doubly-linked list of Student records
 * Student Record Management System
 */

#ifndef LINKED_LIST_H
#define LINKED_LIST_H

#include "student.h"

/* ─── Node ───────────────────────────────────────────────────────────────── */
typedef struct LLNode {
    Student       data;
    struct LLNode *prev;
    struct LLNode *next;
} LLNode;

/* ─── List handle ────────────────────────────────────────────────────────── */
typedef struct {
    LLNode *head;
    LLNode *tail;
    int     size;
} LinkedList;

/* ─── API ────────────────────────────────────────────────────────────────── */
void     ll_init(LinkedList *list);
int      ll_insert_front(LinkedList *list, const Student *s);
int      ll_insert_back(LinkedList *list, const Student *s);
int      ll_insert_sorted(LinkedList *list, const Student *s); /* sorted by student_id */
LLNode  *ll_search_by_id(const LinkedList *list, int id);
LLNode  *ll_search_by_code(const LinkedList *list, const char *code);
int      ll_delete_by_id(LinkedList *list, int id);
void     ll_traverse(const LinkedList *list);
void     ll_traverse_reverse(const LinkedList *list);
int      ll_update(LinkedList *list, int id, const Student *updated);
void     ll_free(LinkedList *list);
int      ll_size(const LinkedList *list);
void     ll_to_array(const LinkedList *list, Student *arr, int capacity);

#endif /* LINKED_LIST_H */

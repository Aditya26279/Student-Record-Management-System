/*
 * linked_list.c — Doubly-linked list implementation
 * Student Record Management System
 */

#include "linked_list.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* ── helpers ───────────────────────────────────────────────────────────── */
static LLNode *make_node(const Student *s) {
    LLNode *node = (LLNode *)malloc(sizeof(LLNode));
    if (!node) { fprintf(stderr, "[LL] malloc failed\n"); return NULL; }
    student_copy(&node->data, s);
    node->prev = node->next = NULL;
    return node;
}

/* ── initialise ─────────────────────────────────────────────────────────── */
void ll_init(LinkedList *list) {
    list->head = list->tail = NULL;
    list->size = 0;
}

/* ── insert at front ────────────────────────────────────────────────────── */
int ll_insert_front(LinkedList *list, const Student *s) {
    LLNode *node = make_node(s);
    if (!node) return -1;
    node->next = list->head;
    if (list->head) list->head->prev = node;
    else            list->tail = node;
    list->head = node;
    list->size++;
    return 0;
}

/* ── insert at back ─────────────────────────────────────────────────────── */
int ll_insert_back(LinkedList *list, const Student *s) {
    LLNode *node = make_node(s);
    if (!node) return -1;
    node->prev = list->tail;
    if (list->tail) list->tail->next = node;
    else            list->head = node;
    list->tail = node;
    list->size++;
    return 0;
}

/* ── insert (keep ascending student_id order) ───────────────────────────── */
int ll_insert_sorted(LinkedList *list, const Student *s) {
    if (!list->head || s->student_id <= list->head->data.student_id)
        return ll_insert_front(list, s);
    if (s->student_id >= list->tail->data.student_id)
        return ll_insert_back(list, s);

    LLNode *cur = list->head->next;
    while (cur && cur->data.student_id < s->student_id) cur = cur->next;

    LLNode *node = make_node(s);
    if (!node) return -1;

    node->prev = cur->prev;
    node->next = cur;
    cur->prev->next = node;
    cur->prev = node;
    list->size++;
    return 0;
}

/* ── search by student_id ───────────────────────────────────────────────── */
LLNode *ll_search_by_id(const LinkedList *list, int id) {
    LLNode *cur = list->head;
    while (cur) {
        if (cur->data.student_id == id) return cur;
        cur = cur->next;
    }
    return NULL;
}

/* ── search by student_code ─────────────────────────────────────────────── */
LLNode *ll_search_by_code(const LinkedList *list, const char *code) {
    LLNode *cur = list->head;
    while (cur) {
        if (strcmp(cur->data.student_code, code) == 0) return cur;
        cur = cur->next;
    }
    return NULL;
}

/* ── delete by student_id ───────────────────────────────────────────────── */
int ll_delete_by_id(LinkedList *list, int id) {
    LLNode *node = ll_search_by_id(list, id);
    if (!node) return -1;

    if (node->prev) node->prev->next = node->next;
    else            list->head       = node->next;

    if (node->next) node->next->prev = node->prev;
    else            list->tail       = node->prev;

    free(node);
    list->size--;
    return 0;
}

/* ── update ─────────────────────────────────────────────────────────────── */
int ll_update(LinkedList *list, int id, const Student *updated) {
    LLNode *node = ll_search_by_id(list, id);
    if (!node) return -1;
    student_copy(&node->data, updated);
    return 0;
}

/* ── forward traversal ──────────────────────────────────────────────────── */
void ll_traverse(const LinkedList *list) {
    printf("\n=== Linked List (%d records) ===\n", list->size);
    if (!list->head) { printf("  [empty]\n"); return; }
    LLNode *cur = list->head;
    while (cur) { student_print(&cur->data); cur = cur->next; }
}

/* ── reverse traversal ───────────────────────────────────────────────────── */
void ll_traverse_reverse(const LinkedList *list) {
    printf("\n=== Linked List — Reverse (%d records) ===\n", list->size);
    if (!list->tail) { printf("  [empty]\n"); return; }
    LLNode *cur = list->tail;
    while (cur) { student_print(&cur->data); cur = cur->prev; }
}

/* ── size ────────────────────────────────────────────────────────────────── */
int ll_size(const LinkedList *list) { return list->size; }

/* ── dump list to flat array (caller allocates) ─────────────────────────── */
void ll_to_array(const LinkedList *list, Student *arr, int capacity) {
    int  i   = 0;
    LLNode *cur = list->head;
    while (cur && i < capacity) {
        student_copy(&arr[i++], &cur->data);
        cur = cur->next;
    }
}

/* ── free all nodes ─────────────────────────────────────────────────────── */
void ll_free(LinkedList *list) {
    LLNode *cur = list->head;
    while (cur) {
        LLNode *next = cur->next;
        free(cur);
        cur = next;
    }
    ll_init(list);
}

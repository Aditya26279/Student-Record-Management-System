/*
 * bst.c — Binary Search Tree implementation
 * Student Record Management System
 */

#include "bst.h"
#include <stdio.h>
#include <stdlib.h>

/* ── helpers ───────────────────────────────────────────────────────────── */
static BSTNode *make_node(const Student *s) {
    BSTNode *n = (BSTNode *)malloc(sizeof(BSTNode));
    if (!n) { fprintf(stderr, "[BST] malloc failed\n"); return NULL; }
    student_copy(&n->data, s);
    n->left = n->right = NULL;
    return n;
}

static BSTNode *insert_r(BSTNode *node, const Student *s, int *ok) {
    if (!node) { *ok = 1; return make_node(s); }
    if (s->student_id < node->data.student_id)
        node->left  = insert_r(node->left,  s, ok);
    else if (s->student_id > node->data.student_id)
        node->right = insert_r(node->right, s, ok);
    /* duplicate → ignore */
    return node;
}

static BSTNode *min_node(BSTNode *node) {
    while (node->left) node = node->left;
    return node;
}

static BSTNode *delete_r(BSTNode *node, int id, int *ok) {
    if (!node) return NULL;
    if (id < node->data.student_id)
        node->left  = delete_r(node->left,  id, ok);
    else if (id > node->data.student_id)
        node->right = delete_r(node->right, id, ok);
    else {
        *ok = 1;
        if (!node->left)  { BSTNode *t = node->right; free(node); return t; }
        if (!node->right) { BSTNode *t = node->left;  free(node); return t; }
        /* two children: replace with in-order successor */
        BSTNode *succ = min_node(node->right);
        student_copy(&node->data, &succ->data);
        node->right = delete_r(node->right, succ->data.student_id, ok);
    }
    return node;
}

static BSTNode *search_r(BSTNode *node, int id) {
    if (!node || node->data.student_id == id) return node;
    return (id < node->data.student_id)
           ? search_r(node->left,  id)
           : search_r(node->right, id);
}

static int height_r(const BSTNode *node) {
    if (!node) return 0;
    int l = height_r(node->left);
    int r = height_r(node->right);
    return 1 + (l > r ? l : r);
}

static void inorder_r(const BSTNode *node) {
    if (!node) return;
    inorder_r(node->left);
    student_print(&node->data);
    inorder_r(node->right);
}

static void preorder_r(const BSTNode *node) {
    if (!node) return;
    student_print(&node->data);
    preorder_r(node->left);
    preorder_r(node->right);
}

static void postorder_r(const BSTNode *node) {
    if (!node) return;
    postorder_r(node->left);
    postorder_r(node->right);
    student_print(&node->data);
}

static void range_r(const BSTNode *node, int lo, int hi,
                    Student *out, int capacity, int *count) {
    if (!node || *count >= capacity) return;
    if (node->data.student_id > lo)
        range_r(node->left,  lo, hi, out, capacity, count);
    if (node->data.student_id >= lo && node->data.student_id <= hi) {
        student_copy(&out[(*count)++], &node->data);
    }
    if (node->data.student_id < hi)
        range_r(node->right, lo, hi, out, capacity, count);
}

static void free_r(BSTNode *node) {
    if (!node) return;
    free_r(node->left);
    free_r(node->right);
    free(node);
}

/* ── public API ─────────────────────────────────────────────────────────── */
void bst_init(BST *tree) { tree->root = NULL; tree->size = 0; }

int bst_insert(BST *tree, const Student *s) {
    int ok = 0;
    tree->root = insert_r(tree->root, s, &ok);
    if (ok) tree->size++;
    return ok ? 0 : -1;   /* -1 = duplicate */
}

BSTNode *bst_search(const BST *tree, int id) {
    return search_r(tree->root, id);
}

int bst_delete(BST *tree, int id) {
    int ok = 0;
    tree->root = delete_r(tree->root, id, &ok);
    if (ok) tree->size--;
    return ok ? 0 : -1;
}

void bst_inorder(const BST *tree) {
    printf("\n=== BST In-order (%d records) ===\n", tree->size);
    inorder_r(tree->root);
}

void bst_preorder(const BST *tree) {
    printf("\n=== BST Pre-order (%d records) ===\n", tree->size);
    preorder_r(tree->root);
}

void bst_postorder(const BST *tree) {
    printf("\n=== BST Post-order (%d records) ===\n", tree->size);
    postorder_r(tree->root);
}

int bst_height(const BST *tree) { return height_r(tree->root); }
int bst_size(const BST *tree)   { return tree->size; }

int bst_range_search(const BST *tree, int lo, int hi,
                     Student *out, int capacity) {
    int count = 0;
    range_r(tree->root, lo, hi, out, capacity, &count);
    return count;
}

void bst_free(BST *tree) {
    free_r(tree->root);
    bst_init(tree);
}

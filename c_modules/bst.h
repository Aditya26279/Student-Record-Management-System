/*
 * bst.h — Binary Search Tree keyed on student_id
 * Student Record Management System
 */

#ifndef BST_H
#define BST_H

#include "student.h"

/* ─── Node ───────────────────────────────────────────────────────────────── */
typedef struct BSTNode {
    Student        data;
    struct BSTNode *left;
    struct BSTNode *right;
} BSTNode;

/* ─── Tree handle ────────────────────────────────────────────────────────── */
typedef struct {
    BSTNode *root;
    int      size;
} BST;

/* ─── API ────────────────────────────────────────────────────────────────── */
void     bst_init(BST *tree);
int      bst_insert(BST *tree, const Student *s);
BSTNode *bst_search(const BST *tree, int id);
int      bst_delete(BST *tree, int id);
void     bst_inorder(const BST *tree);          /* ascending by id  */
void     bst_preorder(const BST *tree);
void     bst_postorder(const BST *tree);
int      bst_height(const BST *tree);
void     bst_free(BST *tree);
int      bst_size(const BST *tree);

/* range search: collect students with id in [lo, hi] */
int      bst_range_search(const BST *tree, int lo, int hi,
                          Student *out, int capacity);

#endif /* BST_H */

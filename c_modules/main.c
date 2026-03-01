/*
 * main.c — Test driver for all C data-structure modules
 * Student Record Management System
 *
 * Compile:  gcc -o srms_test main.c linked_list.c bst.c hash_table.c sorting.c searching.c file_ops.c -lm
 * Or:       make
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "student.h"
#include "linked_list.h"
#include "bst.h"
#include "hash_table.h"
#include "sorting.h"
#include "searching.h"
#include "file_ops.h"

/* ─── Helpers ────────────────────────────────────────────────────────────── */
#define PRINT_SECTION(name) \
    printf("\n\033[1;36m" "══════════════════════════════════════════\n" \
           " " name "\n" \
           "══════════════════════════════════════════\033[0m\n")

#define PASS(msg) printf("  \033[1;32m[PASS]\033[0m %s\n", msg)
#define FAIL(msg) printf("  \033[1;31m[FAIL]\033[0m %s\n", msg)
#define CHECK(cond, msg) do { if (cond) PASS(msg); else FAIL(msg); } while(0)

static Student make_student(int id, const char *code,
                            const char *first, const char *last,
                            const char *dept, float gpa) {
    Student s;
    memset(&s, 0, sizeof(s));
    s.student_id = id;
    strncpy(s.student_code, code,  MAX_CODE  - 1);
    strncpy(s.first_name,   first, MAX_NAME  - 1);
    strncpy(s.last_name,    last,  MAX_NAME  - 1);
    strncpy(s.department,   dept,  MAX_DEPT  - 1);
    snprintf(s.email, MAX_EMAIL, "%s.%s@student.edu", first, last);
    strncpy(s.status, "active", MAX_STATUS - 1);
    s.gpa = gpa;
    return s;
}

/* ─── Sample data ────────────────────────────────────────────────────────── */
#define N_SAMPLES 10
static Student samples[N_SAMPLES];

static void init_samples(void) {
    samples[0] = make_student(5,  "STU20240005", "Karan",    "Singh",   "IT",  7.80f);
    samples[1] = make_student(2,  "STU20240002", "Priyanka", "Gupta",   "CS",  8.60f);
    samples[2] = make_student(8,  "STU20240008", "Meera",    "Nair",    "CS",  9.10f);
    samples[3] = make_student(1,  "STU20240001", "Aditya",   "Sharma",  "CS",  8.20f);
    samples[4] = make_student(10, "STU20240010", "Divya",    "Kumar",   "IT",  7.60f);
    samples[5] = make_student(3,  "STU20240003", "Rohan",    "Mehta",   "CS",  6.30f);
    samples[6] = make_student(7,  "STU20240007", "Vikram",   "Reddy",   "EC",  7.20f);
    samples[7] = make_student(4,  "STU20240004", "Sneha",    "Patil",   "IT",  8.40f);
    samples[8] = make_student(6,  "STU20240006", "Ananya",   "Iyer",    "EC",  8.00f);
    samples[9] = make_student(9,  "STU20240009", "Arjun",    "Patel",   "CS",  7.40f);
}

/* ─── Tests ──────────────────────────────────────────────────────────────── */

static void test_linked_list(void) {
    PRINT_SECTION("1. LINKED LIST");
    LinkedList list;
    ll_init(&list);

    for (int i = 0; i < N_SAMPLES; i++) ll_insert_sorted(&list, &samples[i]);
    printf("  Inserted %d records (sorted).\n", ll_size(&list));
    CHECK(ll_size(&list) == N_SAMPLES, "Insert sorted — correct size");

    ll_traverse(&list);

    /* Search */
    LLNode *found = ll_search_by_id(&list, 5);
    CHECK(found && strcmp(found->data.first_name, "Karan") == 0,
          "Search by ID=5 → Karan Singh");

    LLNode *notfound = ll_search_by_id(&list, 99);
    CHECK(notfound == NULL, "Search by ID=99 → NULL (not found)");

    /* search by code */
    LLNode *bycode = ll_search_by_code(&list, "STU20240008");
    CHECK(bycode && strcmp(bycode->data.first_name, "Meera") == 0,
          "Search by code STU20240008 → Meera Nair");

    /* Delete */
    int rc = ll_delete_by_id(&list, 3);
    CHECK(rc == 0 && ll_size(&list) == N_SAMPLES - 1, "Delete ID=3 — size decremented");

    /* Reverse traversal */
    ll_traverse_reverse(&list);

    ll_free(&list);
    CHECK(ll_size(&list) == 0, "Free — size reset to 0");
}

static void test_bst(void) {
    PRINT_SECTION("2. BINARY SEARCH TREE");
    BST tree;
    bst_init(&tree);

    for (int i = 0; i < N_SAMPLES; i++) bst_insert(&tree, &samples[i]);
    CHECK(bst_size(&tree) == N_SAMPLES, "Insert — correct size");
    printf("  Tree height: %d\n", bst_height(&tree));

    bst_inorder(&tree);

    /* Search */
    BSTNode *found = bst_search(&tree, 8);
    CHECK(found && strcmp(found->data.first_name, "Meera") == 0,
          "Search ID=8 → Meera Nair");

    /* Duplicate insert */
    int dup = bst_insert(&tree, &samples[0]);
    CHECK(dup == -1, "Duplicate insert rejected");

    /* Range search */
    Student range_out[10];
    int cnt = bst_range_search(&tree, 3, 7, range_out, 10);
    printf("  Range [3,7]: %d students found\n", cnt);
    CHECK(cnt == 5, "Range search [3,7] → 5 students");

    /* Delete */
    bst_delete(&tree, 5);
    CHECK(bst_size(&tree) == N_SAMPLES - 1, "Delete ID=5 — size decremented");
    CHECK(bst_search(&tree, 5) == NULL, "Deleted ID=5 not found");

    bst_free(&tree);
    CHECK(bst_size(&tree) == 0, "Free — size reset to 0");
}

static void test_hash_table(void) {
    PRINT_SECTION("3. HASH TABLE");
    HashTable *ht = ht_create(HT_DEFAULT_SIZE);

    for (int i = 0; i < N_SAMPLES; i++) ht_insert(ht, &samples[i]);
    CHECK(ht_size(ht) == N_SAMPLES, "Insert — correct size");
    printf("  Load factor: %.3f\n", ht_load_factor(ht));

    /* Search */
    Student *s = ht_search(ht, 4);
    CHECK(s && strcmp(s->first_name, "Sneha") == 0, "Search ID=4 → Sneha Patil");

    Student *miss = ht_search(ht, 99);
    CHECK(miss == NULL, "Search ID=99 → NULL");

    /* Update */
    Student updated = samples[1];
    updated.gpa = 9.50f;
    ht_update(ht, &updated);
    Student *upd_check = ht_search(ht, samples[1].student_id);
    CHECK(upd_check && upd_check->gpa == 9.50f, "Update GPA → 9.50");

    /* Delete */
    ht_delete(ht, 10);
    CHECK(ht_size(ht) == N_SAMPLES - 1, "Delete ID=10 — size decremented");
    CHECK(ht_search(ht, 10) == NULL, "Deleted ID=10 not found");

    ht_print(ht);
    ht_destroy(ht);
    PASS("Hash table destroyed");
}

static void test_sorting(void) {
    PRINT_SECTION("4. SORTING ALGORITHMS");

    Student arr[N_SAMPLES];

    /* --- Quick Sort by ID --- */
    memcpy(arr, samples, sizeof(samples));
    quick_sort(arr, N_SAMPLES, cmp_by_id);
    int sorted = 1;
    for (int i = 1; i < N_SAMPLES; i++)
        if (arr[i].student_id < arr[i-1].student_id) { sorted = 0; break; }
    CHECK(sorted, "Quick Sort by ID — ascending order");

    /* --- Merge Sort by GPA desc --- */
    memcpy(arr, samples, sizeof(samples));
    merge_sort(arr, N_SAMPLES, cmp_by_gpa_desc);
    sorted = 1;
    for (int i = 1; i < N_SAMPLES; i++)
        if (arr[i].gpa > arr[i-1].gpa) { sorted = 0; break; }
    CHECK(sorted, "Merge Sort by GPA (desc) — correct order");
    printf("  Top GPA: %.2f (%s %s)\n", arr[0].gpa, arr[0].first_name, arr[0].last_name);

    /* --- Bubble Sort by name --- */
    memcpy(arr, samples, sizeof(samples));
    bubble_sort(arr, N_SAMPLES, cmp_by_name);
    printf("  Bubble sort (name): %s → %s\n",
           arr[0].last_name, arr[N_SAMPLES-1].last_name);
    CHECK(strcmp(arr[0].last_name, arr[N_SAMPLES-1].last_name) <= 0,
          "Bubble Sort by name — lexicographic order");

    /* --- Benchmark all algorithms --- */
    printf("\n  Benchmarks (%d records):\n", N_SAMPLES);
    printf("    Bubble:    %.6f s\n", sort_benchmark(bubble_sort,    samples, N_SAMPLES, cmp_by_id));
    printf("    Selection: %.6f s\n", sort_benchmark(selection_sort, samples, N_SAMPLES, cmp_by_id));
    printf("    Insertion: %.6f s\n", sort_benchmark(insertion_sort, samples, N_SAMPLES, cmp_by_id));
    printf("    Merge:     %.6f s\n", sort_benchmark(merge_sort,     samples, N_SAMPLES, cmp_by_id));
    printf("    Quick:     %.6f s\n", sort_benchmark(quick_sort,     samples, N_SAMPLES, cmp_by_id));
}

static void test_searching(void) {
    PRINT_SECTION("5. SEARCHING ALGORITHMS");

    /* Sort by ID for binary search */
    Student sorted_arr[N_SAMPLES];
    memcpy(sorted_arr, samples, sizeof(samples));
    quick_sort(sorted_arr, N_SAMPLES, cmp_by_id);

    /* Linear search */
    int idx = linear_search_by_id(sorted_arr, N_SAMPLES, 7);
    CHECK(idx >= 0 && sorted_arr[idx].student_id == 7, "Linear search ID=7 → found");

    idx = linear_search_by_id(sorted_arr, N_SAMPLES, 99);
    CHECK(idx == -1, "Linear search ID=99 → -1 (not found)");

    idx = linear_search_by_name(sorted_arr, N_SAMPLES, "meera");
    CHECK(idx >= 0, "Linear search name='meera' (case-insensitive) → found");

    /* Binary search by ID */
    idx = binary_search_by_id(sorted_arr, N_SAMPLES, 6);
    CHECK(idx >= 0 && sorted_arr[idx].student_id == 6, "Binary search ID=6 → found");

    idx = binary_search_by_id(sorted_arr, N_SAMPLES, 42);
    CHECK(idx == -1, "Binary search ID=42 → -1 (not found)");

    /* Department filter */
    int indices[N_SAMPLES];
    int cnt = find_by_department(sorted_arr, N_SAMPLES, "CS", indices, N_SAMPLES);
    printf("  CS students: %d\n", cnt);
    CHECK(cnt == 4, "Department filter 'CS' → 4 students");

    /* GPA range */
    Student gpa_out[N_SAMPLES];
    cnt = find_by_gpa_range(sorted_arr, N_SAMPLES, 8.0f, 10.0f, gpa_out, N_SAMPLES);
    printf("  GPA [8.0–10.0] matches: %d\n", cnt);
    CHECK(cnt >= 1, "GPA range [8.0,10.0] → at least 1 student");
}

static void test_file_ops(void) {
    PRINT_SECTION("6. FILE OPERATIONS");

    const char *bin_path = "test_records.bin";
    const char *csv_path = "test_records.csv";
    const char *bak_path = "test_records_backup.bin";

    /* Save binary */
    int rc = file_save_binary(bin_path, samples, N_SAMPLES);
    CHECK(rc == 0, "Binary save → success");

    /* Count without full load */
    int cnt = file_count_records(bin_path);
    CHECK(cnt == N_SAMPLES, "Binary count → correct");

    /* Load binary */
    Student loaded[N_SAMPLES + 5];
    int n = file_load_binary(bin_path, loaded, N_SAMPLES + 5);
    CHECK(n == N_SAMPLES, "Binary load → correct count");
    CHECK(loaded[0].student_id == samples[0].student_id, "First record ID matches");

    /* Backup */
    rc = file_backup(bin_path, bak_path);
    CHECK(rc == 0, "Backup → success");

    /* Append */
    Student extra = make_student(11, "STU20240011", "Test", "Student", "CS", 7.00f);
    file_append_record(bin_path, &extra);
    cnt = file_count_records(bin_path);
    CHECK(cnt == N_SAMPLES + 1, "Append record → count incremented");

    /* CSV round-trip */
    rc = file_save_csv(csv_path, samples, N_SAMPLES);
    CHECK(rc == 0, "CSV save → success");

    Student csv_loaded[N_SAMPLES + 5];
    n = file_load_csv(csv_path, csv_loaded, N_SAMPLES + 5);
    CHECK(n == N_SAMPLES, "CSV load → correct count");
    CHECK(csv_loaded[0].student_id == samples[0].student_id,
          "CSV round-trip — first ID preserved");

    /* Clean up test files */
    remove(bin_path); remove(csv_path); remove(bak_path);
    PASS("Test files cleaned up");
}

/* ─── Main ───────────────────────────────────────────────────────────────── */
int main(void) {
    printf("\033[1;35m");
    printf("╔══════════════════════════════════════════╗\n");
    printf("║  Student Record Management System — C   ║\n");
    printf("║  Data Structures & Algorithms Test Suite ║\n");
    printf("╚══════════════════════════════════════════╝\n");
    printf("\033[0m");

    init_samples();

    test_linked_list();
    test_bst();
    test_hash_table();
    test_sorting();
    test_searching();
    test_file_ops();

    printf("\n\033[1;32m══════════════════════════════════════════\n");
    printf(" All tests complete!\n");
    printf("══════════════════════════════════════════\033[0m\n\n");
    return 0;
}

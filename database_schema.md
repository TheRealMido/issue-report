# Relational Schema Model (Academic Grid)

### USERS Table
| <u>user_id</u> (PK) | name | email | role |
| :--- | :--- | :--- | :--- |

### CATEGORIES Table
| <u>category_id</u> (PK) | name |
| :--- | :--- |

### ISSUES Table
| <u>issue_id</u> (PK) | title | description | *category_id* (FK) | *user_id* (FK) | location | status | date_submitted |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |

### STATUS_UPDATES Table
| <u>update_id</u> (PK) | *issue_id* (FK) | updated_by (FK) | old_status | new_status | note | update_time |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |

### VOTES Table
| <u>vote_id</u> (PK) | *user_id* (FK) | *issue_id* (FK) |
| :--- | :--- | :--- |

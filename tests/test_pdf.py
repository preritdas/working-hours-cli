import export

tasks = [
    {
        "Date": "2022-08-15 18-30",
        "Deliverable": "https://obscurelink-my.sharepoint.com/:f:/p/john_doe/Er6AaaouTAlPoXZzCcB1njXBabcdeFGBxbvzAtBCDeNkOp?e=XYZaBC",
        "Hours": 1.05,
        "Task": "Alex Smith: Session 1 Lesson and Feedback",
        "key": "11aa1aa11111",
    },
    {
        "Date": "2022-08-09 16-00",
        "Deliverable": "https://obscurelink-my.sharepoint.com/:b:/p/john_doe/EZkABCa-5gVHwxP6aaabVDMB67rTuv2lDT1sEFEF45tvOp?e=a5n7Bb",
        "Hours": 1.5,
        "Task": "Chris Brown: Session 3 Lesson and Homework",
        "key": "422kc3ysjy51",
    },
    {
        "Date": "2022-08-28 15-30",
        "Deliverable": "https://obscurelink-my.sharepoint.com/:b:/p/john_doe/ES8ZaDEFMomDT9P35SSAwSvBjoo_HGvWf9x_6DEE5eY2Tr?e=CDbvwA",
        "Hours": 1.1,
        "Task": "Chris Brown: Session 5 Lesson and Feedback",
        "key": "6e6m691ilsss",
    },
    {
        "Date": "2022-08-28 12-00",
        "Deliverable": "https://obscurelink-my.sharepoint.com/:b:/p/john_doe/EZEAaJzz2dBBlk8ITdd5i9vB6ef-789dOpZXQ8ZCH9-Plr?e=M5NwfY",
        "Hours": 1.3,
        "Task": "Molly Gray: Session 4 Lesson And Homework",
        "key": "8xqz3xks699t",
    },
    {
        "Date": "2022-08-10 07-00",
        "Deliverable": "https://obscurelink-my.sharepoint.com/:f:/p/john_doe/Egh7pDEFj5ZMpr3u_YZj1ZQBb9DEu7PyrpOPzXoJKZpxlB?e=GFGvkp",
        "Hours": 1.1,
        "Task": "Molly Gray: Session 2 Lesson and Feedback",
        "key": "0t5go1wwdxpg",
    },
    {
        "Date": "2022-08-17 19-00",
        "Deliverable": "https://obscurelink-my.sharepoint.com/:b:/p/john_doe/Ea9ghik5LnRGpgUVZZcZY45CDEFZeZYOhA01UVyXMJ_hWl?e=kGHFij",
        "Hours": 1.2,
        "Task": "Molly Gray: Session 3 Lesson And Feedback",
        "key": "c7kf6p58zst4",
    },
    {
        "Date": "2022-08-02 16-00",
        "Deliverable": "Session 2 Feedback and Homework on Portal",
        "Hours": 1.38,
        "Task": "Chris Brown: Session 2 Lesson and Resources",
        "key": "p1mor6j7e1p5",
    },
    {
        "Date": "2022-08-21 15-30",
        "Deliverable": "https://obscurelink-my.sharepoint.com/:b:/p/john_doe/ERdQkQRwJeRAtXYLcjc87RoC39b7L3qpnyPBIzcxvnhhls?e=5Z6dDD",
        "Hours": 1.3,
        "Task": "Chris Brown: Session 4 Lesson And Feedback",
        "key": "t2zf8gdz76pb",
    },
    {
        "Date": "2022-08-03 19-00",
        "Deliverable": "Session 1 Feedback and Homework on Portal",
        "Hours": 1.45,
        "Task": "Molly Gray: Session 1 Lesson and Resources",
        "key": "tb5jcmbb47u0",
    },
    {
        "Date": "2022-08-22 18-30",
        "Deliverable": "https://obscurelink-my.sharepoint.com/:b:/p/john_doe/EZE6Lzt6HgGOnJeZV9MUXFwCZ36SGPQfzVWwOPVfhJP7XR?e=8hlxvH",
        "Hours": 1.2,
        "Task": "Alex Smith: Session 2 Lesson And Feedback",
        "key": "vphmev43vik8",
    },
]

monthyear = "8-2022"


def test_export_tasks():
    export.export_tasks(tasks, monthyear)

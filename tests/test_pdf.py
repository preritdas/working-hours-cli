import export

tasks = [
    {
        "Date": "2022-08-15 18-30",
        "Deliverable": "https://seewessential-my.sharepoint.com/:f:/p/michael_ma/Er6OMmouTAlGoYAzJcB2njYBfsgqaJBBybvxItADSuMjIg?e=TDWzaY",
        "Hours": 1.05,
        "Task": "Michelle Ye: Session 1 Lesson and Feedback",
        "key": "16wd3ui94919",
    },
    {
        "Date": "2022-08-09 16-00",
        "Deliverable": "https://seewessential-my.sharepoint.com/:b:/p/michael_ma/EZkAHRt-5gVHhxP7caaqVEMB67rUca2lBU1sDDEAS5fvNg?e=c5m7Ao",
        "Hours": 1.5,
        "Task": "Daniel Li: Session 3 Lesson and Homework",
        "key": "415lb2xsiy40",
    },
    {
        "Date": "2022-08-28 15-30",
        "Deliverable": "https://seewessential-my.sharepoint.com/:b:/p/michael_ma/ES8ZuEXMomBMr9O36SSRwSgBjii_HFcQf8w_6SCO4dX1Hg?e=BUbuwS",
        "Hours": 1.1,
        "Task": "Daniel Li: Session 5 Lesson and Feedback",
        "key": "5d5l580hlrrr",
    },
    {
        "Date": "2022-08-28 12-00",
        "Deliverable": "https://seewessential-my.sharepoint.com/:b:/p/michael_ma/EZEn4Hqzz1dAik9HTbb6h9gB5ve-709dIoYXC7YBH8-Ofg?e=O4LwfZ",
        "Hours": 1.3,
        "Task": "Kaylee Tom: Session 4 Lesson And Homework",
        "key": "7wpz2whs578s",
    },
    {
        "Date": "2022-08-10 07-00",
        "Deliverable": "https://seewessential-my.sharepoint.com/:f:/p/michael_ma/Egh6pMXhj4ZLor2t_XZj0YQBb9CUc6OxrpHMwYnbJZonkA?e=FLFvku",
        "Hours": 1.1,
        "Task": "Kaylee Tom: Session 2 Lesson and Feedback",
        "key": "9r4fo0vvcwof",
    },
    {
        "Date": "2022-08-17 19-00",
        "Deliverable": "https://seewessential-my.sharepoint.com/:b:/p/michael_ma/Ea8frek4LnREogTRYYcZX34BDRxIeZYOhA90WTyXlE_gVg?e=iDFChj",
        "Hours": 1.2,
        "Task": "Kaylee Tom: Session 3 Lesson And Feedback",
        "key": "b6je5o47zqs3",
    },
    {
        "Date": "2022-08-02 16-00",
        "Deliverable": "Session 2 Feedback and Homework on Portal",
        "Hours": 1.38,
        "Task": "Daniel Li: Session 2 Lesson and Resources",
        "key": "o0lor5i6d0r4",
    },
    {
        "Date": "2022-08-21 15-30",
        "Deliverable": "https://seewessential-my.sharepoint.com/:b:/p/michael_ma/ERcPjPPwIeRAtUXKbjc76QoB38a6K2mpmyQAIzawunhgrg?e=4Y5cZZ",
        "Hours": 1.3,
        "Task": "Daniel Li: Session 4 Lesson And Feedback",
        "key": "s1ze7fcw65oa",
    },
    {
        "Date": "2022-08-03 19-00",
        "Deliverable": "Session 1 Feedback and Homework on Portal",
        "Hours": 1.45,
        "Task": "Kaylee Tom: Session 1 Lesson and Resources",
        "key": "sa4iblga36t9",
    },
    {
        "Date": "2022-08-22 18-30",
        "Deliverable": "https://seewessential-my.sharepoint.com/:b:/p/michael_ma/EZE5Lws5GfFOmJdYW8MUXEwBZ25RFOPfzTUwMNVehIO6WQ?e=7glwuG",
        "Hours": 1.2,
        "Task": "Michelle Ye: Session 2 Lesson And Feedback",
        "key": "uogldu32uhk7",
    },
]

monthyear = "8-2022"


def test_export_tasks():
    export.export_tasks(tasks, monthyear)

# Claude Chat Planning Prompt

Copy this into a Claude Chat conversation to plan your day and generate importable tasks.

---

**Prompt:**

```
It's [TIME] and I need to get the following done today: [LIST YOUR TASKS]

Help me plan a realistic timeline. For each task:
- Estimate how long it'll take
- Suggest a smart order (factor in dependencies, travel, prep time)
- Set a "done by" time based on the timeline
- Assign priority (1=high, 2=medium, 3=low)

Once I review and approve, output ONLY a JSON code block in this exact format:

```json
[
  {
    "title": "Task name",
    "category": "personal",
    "priority": 1,
    "due_date": "2026-03-29",
    "due_time": "18:30",
    "notes": "~30 min. Any details here."
  }
]
```

Rules for the JSON:
- category must be one of: "work", "school", "personal"
- priority: 1 (high), 2 (medium), 3 (low)
- due_date: YYYY-MM-DD format
- due_time: 24-hour HH:MM format (this is the "done by" deadline)
- notes: include estimated duration and any relevant details
- Do NOT include any text outside the JSON code block in your final output
```

---

**Example conversation:**

> It's 5:30 PM and I need to get the following done today: install my TODO printer, set up my work desk with the new KVM switch and cables for 3 PCs, get milk and bread, make burgers on the grill for dinner, and fold the laundry.

Claude will plan it out, then you approve, and it gives you the JSON. Copy the JSON, go to your dashboard, click **Import**, paste, done.

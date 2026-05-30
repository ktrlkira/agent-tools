---
name: task-poller
description: Use when checking for pending tasks in the local agent queue, or when running the scheduled task poll cycle
---

# Task Poller

Check the local task queue for work, execute one task, and report the result including token usage.

## Steps

1. Run: `python3 ~/.hermes/skills/task-poller/scripts/task_helper.py fetch` (calls the API at localhost:8000)
   - Or query directly: `curl -s http://localhost:8000/tasks?status=pending`
   - If no pending tasks, stop.
   - Otherwise, note the task `id`, `description`, and `complexity`.

2. Claim: `python3 ~/.hermes/skills/task-poller/scripts/task_helper.py claim <task_id>`
   - Uses PATCH `/tasks/{task_id}` to set status to `in_progress`
   - Note: API may return `claimed: false` due to race conditions, but task still executes

3. Heartbeat: `curl -s -X PATCH http://localhost:8000/tasks/{task_id}` with status update
   - Call before any operation that may take >1 minute
   - Or use: `python3 ~/.hermes/hermes-agent/vermillion.py heartbeat <task_id>`

4. Execute the task.

5. Report result:
   - Success: `curl -s -X PATCH http://localhost:8000/tasks/{task_id} -H "Content-Type: application/json" -d '{"status":"completed","result":"<result>"}'`
   - Failure: `curl -s -X PATCH http://localhost:8000/tasks/{task_id} -H "Content-Type: application/json" -d '{"status":"failed","error":"<error>"}'`

6. Report token usage and model (always run this — use 0 0 if tokens unavailable, omit model if unknown):

   ```bash
   curl -s -X PATCH http://localhost:8000/tasks/{task_id} \
     -H "Content-Type: application/json" \
     -d '{"tokens_in":<prompt_tokens>,"tokens_out":<completion_tokens>,"cost_usd":0}'
   ```

## Rules

- Execute ONE task per poll cycle.
- Always report tokens (step 6) — use 0 0 if unavailable, never skip.
- Keep result strings under 4000 characters.
- **HEARTBEAT REQUIRED:** Before any tool call that may take >1 minute, call:
  `curl -s -X PATCH http://localhost:8000/tasks/{task_id} -H "Content-Type: application/json" -d '{"status":"in_progress"}'`
  This bumps `updated_at` on the task. Never go more than 5 minutes without heartbeating. Failure to heartbeat will cause the watchdog to kill and requeue the task.
- **AUTH REQUIRED:** Write operations (POST/PATCH) require `Authorization: Bearer $AGENT_API_SECRET` header. Read operations do not require auth.

## Planning phase (complexity: complex tasks only)

If `complexity` is `complex`, do NOT execute directly. Plan first:

1. Claim the task normally (step 2 above), then transition it to split:
   `curl -s -X PATCH http://localhost:8000/tasks/{task_id} -H "Content-Type: application/json" -d '{"status":"split"}'`
2. Break the work into subtasks that each take <25 min to execute.
3. POST each subtask using curl.

**Do not further decompose subtasks** — subtasks must have `complexity: simple`.

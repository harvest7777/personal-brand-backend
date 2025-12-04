# Getting Started

## Prerequisites

- **Supabase CLI**: You'll need the Supabase CLI installed. If you don't have it yet, follow the [installation guide](https://supabase.com/docs/guides/cli/getting-started).
- **Python**: Make sure you have Python installed.

## Setup

### 1. Python Environment

Create a virtual environment and activate it:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 2. Starting Supabase

1. Start the local Supabase instance:

   ```bash
   supabase start
   ```

2. The migration files are already in the project at `supabase/migrations/`. They will be automatically applied when you start Supabase.

3. Once started, you'll see connection details for your local Supabase instance including:
   - API URL
   - Database URL
   - Studio URL (for the Supabase dashboard)

## Running Agents

You can start the agents using Python module syntax:

```bash
# Start the data management agent
python -m wrapped_uagents.wrapped_data_management_agent

# Start the brand agent
python -m wrapped_uagents.wrapped_brand_agent
```

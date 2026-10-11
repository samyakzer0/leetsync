CREATE TABLE IF NOT EXISTS problem_tags (
    problem_date DATE NOT NULL
        REFERENCES problems(problem_date) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL
        REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (problem_date, tag_id)
);

CREATE TABLE IF NOT EXISTS problem_matches (
    problem_date DATE NOT NULL
        REFERENCES problems(problem_date) ON DELETE CASCADE,
    tag_id BIGINT NOT NULL
        REFERENCES tags(id) ON DELETE CASCADE,
    matched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (problem_date, tag_id)
);

CREATE INDEX IF NOT EXISTS idx_problems_problem_id
    ON problems(problem_id);

CREATE INDEX IF NOT EXISTS idx_problem_tags_tag_id
    ON problem_tags(tag_id);

CREATE INDEX IF NOT EXISTS idx_problem_matches_tag_id
    ON problem_matches(tag_id);

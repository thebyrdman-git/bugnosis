export interface Stats {
  total_bugs: number;
  total_users: number;
  total_contributions: number;
  avg_impact: number;
}

export interface Bug {
  repo: string;
  title: string;
  url: string;
  impact_score: number;
  affected_users: number;
  severity: string;
  comments?: number;
  reactions?: number;
}


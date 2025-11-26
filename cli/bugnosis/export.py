"""Export functionality for bugs and stats."""

import json
import csv
from pathlib import Path
from typing import List, Dict
from datetime import datetime


def export_bugs_json(bugs: List[Dict], output_file: str):
    """
    Export bugs to JSON format.
    
    Args:
        bugs: List of bug dictionaries
        output_file: Output file path
    """
    output = {
        'exported_at': datetime.now().isoformat(),
        'total_bugs': len(bugs),
        'bugs': bugs
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)


def export_bugs_csv(bugs: List[Dict], output_file: str):
    """
    Export bugs to CSV format.
    
    Args:
        bugs: List of bug dictionaries
        output_file: Output file path
    """
    if not bugs:
        return
        
    fieldnames = ['repo', 'issue_number', 'title', 'url', 
                  'impact_score', 'affected_users', 'severity', 
                  'discovered_at', 'status']
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for bug in bugs:
            writer.writerow({k: bug.get(k, '') for k in fieldnames})


def export_bugs_markdown(bugs: List[Dict], output_file: str):
    """
    Export bugs to Markdown format.
    
    Args:
        bugs: List of bug dictionaries
        output_file: Output file path
    """
    with open(output_file, 'w') as f:
        f.write("# High-Impact Bugs to Fix\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total bugs: {len(bugs)}\n\n")
        f.write("---\n\n")
        
        for i, bug in enumerate(bugs, 1):
            f.write(f"## {i}. {bug['title']}\n\n")
            f.write(f"**Impact Score:** {bug['impact_score']}/100\n\n")
            f.write(f"**Repository:** {bug['repo']}\n\n")
            f.write(f"**Users Affected:** ~{bug['affected_users']:,}\n\n")
            f.write(f"**Severity:** {bug['severity']}\n\n")
            f.write(f"**Issue:** {bug['url']}\n\n")
            
            if bug.get('status'):
                f.write(f"**Status:** {bug['status']}\n\n")
                
            f.write("---\n\n")


def export_stats_json(stats: Dict, output_file: str):
    """
    Export statistics to JSON format.
    
    Args:
        stats: Statistics dictionary
        output_file: Output file path
    """
    output = {
        'exported_at': datetime.now().isoformat(),
        'stats': stats
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)


def export_leaderboard(contributions: List[Dict], output_file: str):
    """
    Export contributions as leaderboard HTML.
    
    Args:
        contributions: List of contribution dictionaries
        output_file: Output file path
    """
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bugnosis Leaderboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }
        .stat-label {
            color: #7f8c8d;
            margin-top: 5px;
        }
        table {
            width: 100%;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-collapse: collapse;
        }
        th {
            background: #3498db;
            color: white;
            padding: 15px;
            text-align: left;
        }
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #ecf0f1;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .impact-high { color: #e74c3c; font-weight: bold; }
        .impact-medium { color: #f39c12; }
        .impact-low { color: #95a5a6; }
        .footer {
            text-align: center;
            margin-top: 40px;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <h1>Bugnosis Leaderboard</h1>
    <p style="text-align: center; color: #7f8c8d;">
        Last updated: {timestamp}
    </p>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{total_contributions}</div>
            <div class="stat-label">Total Contributions</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_users:,}</div>
            <div class="stat-label">Users Helped</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{avg_impact}</div>
            <div class="stat-label">Average Impact</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{hours_saved:,.0f}h</div>
            <div class="stat-label">Time Saved</div>
        </div>
    </div>
    
    <h2>Recent Contributions</h2>
    <table>
        <thead>
            <tr>
                <th>Repository</th>
                <th>PR</th>
                <th>Impact</th>
                <th>Users Helped</th>
                <th>Date</th>
            </tr>
        </thead>
        <tbody>
            {contributions}
        </tbody>
    </table>
    
    <div class="footer">
        <p>Generated by <a href="https://github.com/thebyrdman-git/bugnosis">Bugnosis</a></p>
    </div>
</body>
</html>
"""
    
    # Calculate stats
    total_contributions = len(contributions)
    total_users = sum(c.get('affected_users', 0) for c in contributions)
    avg_impact = sum(c.get('impact_score', 0) for c in contributions) // max(total_contributions, 1)
    hours_saved = total_users * 0.5
    
    # Generate contribution rows
    rows = []
    for contrib in contributions:
        impact_class = ('impact-high' if contrib.get('impact_score', 0) >= 80 
                       else 'impact-medium' if contrib.get('impact_score', 0) >= 60 
                       else 'impact-low')
        
        row = f"""
            <tr>
                <td><a href="https://github.com/{contrib.get('repo', '')}">{contrib.get('repo', 'N/A')}</a></td>
                <td><a href="{contrib.get('pr_url', '#')}">#{contrib.get('pr_number', 'N/A')}</a></td>
                <td class="{impact_class}">{contrib.get('impact_score', 0)}/100</td>
                <td>~{contrib.get('affected_users', 0):,}</td>
                <td>{contrib.get('submitted_at', 'N/A')[:10]}</td>
            </tr>
        """
        rows.append(row)
    
    # Fill template
    html = html.format(
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_contributions=total_contributions,
        total_users=total_users,
        avg_impact=avg_impact,
        hours_saved=hours_saved,
        contributions=''.join(rows)
    )
    
    with open(output_file, 'w') as f:
        f.write(html)


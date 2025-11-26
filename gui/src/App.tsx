import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { sendNotification } from '@tauri-apps/plugin-notification';
import { listen } from '@tauri-apps/api/event';
import { 
  Search, 
  Eye, 
  List, 
  Plus,
  Play,
  BarChart3
} from 'lucide-react';
import './App.css';

interface Stats {
  total_bugs: number;
  total_users: number;
  total_contributions: number;
  avg_impact: number;
}

function App() {
  const [activeTab, setActiveTab] = useState('scan');
  const [repoInput, setRepoInput] = useState('');
  const [minImpact, setMinImpact] = useState(70);
  const [scanResult, setScanResult] = useState('');
  const [savedBugs, setSavedBugs] = useState('');
  const [stats, setStats] = useState<Stats | null>(null);
  const [watchedRepos, setWatchedRepos] = useState<string[]>([]);
  const [insights, setInsights] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadWatchedRepos();
    loadStats();
    
    // Listen for tray scan trigger
    const unlisten = listen('trigger-scan', () => {
      handleScanWatched();
    });
    
    return () => {
      unlisten.then(fn => fn());
    };
  }, []);

  const loadWatchedRepos = async () => {
    try {
      const result = await invoke<string>('get_watched_repos');
      // Parse the output to extract repo names
      const repos = result.split('\n')
        .filter(line => line.trim().startsWith('-'))
        .map(line => line.replace(/^[\s-]+/, '').trim());
      setWatchedRepos(repos);
    } catch (error) {
      console.error('Failed to load watched repos:', error);
    }
  };

  const loadStats = async () => {
    try {
      const result = await invoke<string>('get_stats');
      // Parse stats from output
      const lines = result.split('\n');
      const bugsLine = lines.find(l => l.includes('Bugs tracked:'));
      const contribLine = lines.find(l => l.includes('Contributions:'));
      const usersLine = lines.find(l => l.includes('Users helped:'));
      const impactLine = lines.find(l => l.includes('Average impact:'));
      
      if (bugsLine && contribLine && usersLine && impactLine) {
        setStats({
          total_bugs: parseInt(bugsLine.split(':')[1].trim()) || 0,
          total_contributions: parseInt(contribLine.split(':')[1].trim()) || 0,
          total_users: parseInt(usersLine.split(':')[1].replace(/,/g, '').trim()) || 0,
          avg_impact: parseInt(impactLine.split(':')[1].split('/')[0].trim()) || 0,
        });
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleScan = async () => {
    if (!repoInput.trim()) {
      alert('Please enter a repository name (owner/repo)');
      return;
    }

    setLoading(true);
    try {
      const result = await invoke<string>('scan_repo', {
        repo: repoInput,
        minImpact: minImpact
      });
      setScanResult(result);
      await sendNotification({
        title: 'Scan Complete',
        body: `Scanned ${repoInput}`
      });
      loadStats();
    } catch (error) {
      setScanResult(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAddWatch = async () => {
    if (!repoInput.trim()) {
      alert('Please enter a repository name (owner/repo)');
      return;
    }

    setLoading(true);
    try {
      await invoke<string>('add_watched_repo', { repo: repoInput });
      await loadWatchedRepos();
      setRepoInput('');
      await sendNotification({
        title: 'Repository Added',
        body: `Now watching ${repoInput}`
      });
    } catch (error) {
      alert(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleScanWatched = async () => {
    setLoading(true);
    try {
      const result = await invoke<string>('scan_watched');
      setScanResult(result);
      await sendNotification({
        title: 'Watch Scan Complete',
        body: 'Scanned all watched repositories'
      });
      loadStats();
    } catch (error) {
      setScanResult(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadSaved = async () => {
    setLoading(true);
    try {
      const result = await invoke<string>('get_saved_bugs', {
        minImpact: minImpact
      });
      setSavedBugs(result);
    } catch (error) {
      setSavedBugs(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadInsights = async () => {
    setLoading(true);
    try {
      const result = await invoke<string>('get_insights', {
        minImpact: minImpact
      });
      setInsights(result);
    } catch (error) {
      setInsights(`Error: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">
            Bugnosis
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Find high-impact bugs to fix in open source projects
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {stats.total_bugs}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400">
                Bugs Tracked
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {stats.total_contributions}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400">
                Contributions
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {stats.total_users.toLocaleString()}
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400">
                Users Helped
              </div>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-sm">
              <div className="text-2xl font-bold text-slate-900 dark:text-white">
                {stats.avg_impact}/100
              </div>
              <div className="text-sm text-slate-600 dark:text-slate-400">
                Avg Impact
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="flex space-x-2 mb-6">
          <TabButton
            icon={<Search size={18} />}
            label="Scan"
            active={activeTab === 'scan'}
            onClick={() => setActiveTab('scan')}
          />
          <TabButton
            icon={<Eye size={18} />}
            label="Watch List"
            active={activeTab === 'watch'}
            onClick={() => setActiveTab('watch')}
          />
          <TabButton
            icon={<List size={18} />}
            label="Saved Bugs"
            active={activeTab === 'saved'}
            onClick={() => setActiveTab('saved')}
          />
          <TabButton
            icon={<BarChart3 size={18} />}
            label="Insights"
            active={activeTab === 'insights'}
            onClick={() => setActiveTab('insights')}
          />
        </div>

        {/* Content */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-6">
          {activeTab === 'scan' && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-4">
                Scan Repository
              </h2>
              
              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Repository (owner/repo)
                  </label>
                  <input
                    type="text"
                    value={repoInput}
                    onChange={(e) => setRepoInput(e.target.value)}
                    placeholder="pytorch/pytorch"
                    className="w-full px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Minimum Impact Score: {minImpact}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={minImpact}
                    onChange={(e) => setMinImpact(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <button
                  onClick={handleScan}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <Search size={18} />
                  <span>{loading ? 'Scanning...' : 'Scan Repository'}</span>
                </button>
              </div>

              {scanResult && (
                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4 mt-4">
                  <pre className="text-sm text-slate-800 dark:text-slate-200 whitespace-pre-wrap font-mono">
                    {scanResult}
                  </pre>
                </div>
              )}
            </div>
          )}

          {activeTab === 'watch' && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-4">
                Watch List
              </h2>

              <div className="space-y-4 mb-6">
                <div className="flex space-x-2">
                  <input
                    type="text"
                    value={repoInput}
                    onChange={(e) => setRepoInput(e.target.value)}
                    placeholder="owner/repo"
                    className="flex-1 px-4 py-2 border border-slate-300 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-slate-700 dark:text-white"
                  />
                  <button
                    onClick={handleAddWatch}
                    disabled={loading}
                    className="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg flex items-center space-x-2 disabled:opacity-50"
                  >
                    <Plus size={18} />
                    <span>Add</span>
                  </button>
                </div>

                <button
                  onClick={handleScanWatched}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <Play size={18} />
                  <span>{loading ? 'Scanning...' : 'Scan All Watched'}</span>
                </button>
              </div>

              <div className="space-y-2">
                <h3 className="font-medium text-slate-900 dark:text-white mb-2">
                  Watched Repositories ({watchedRepos.length})
                </h3>
                {watchedRepos.length === 0 ? (
                  <p className="text-slate-600 dark:text-slate-400 text-sm">
                    No repositories being watched. Add one above!
                  </p>
                ) : (
                  watchedRepos.map((repo, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-50 dark:bg-slate-900 rounded-lg p-3 flex items-center justify-between"
                    >
                      <span className="text-slate-800 dark:text-slate-200">
                        {repo}
                      </span>
                    </div>
                  ))
                )}
              </div>

              {scanResult && (
                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4 mt-4">
                  <pre className="text-sm text-slate-800 dark:text-slate-200 whitespace-pre-wrap font-mono">
                    {scanResult}
                  </pre>
                </div>
              )}
            </div>
          )}

          {activeTab === 'saved' && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-4">
                Saved Bugs
              </h2>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Minimum Impact Score: {minImpact}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={minImpact}
                    onChange={(e) => setMinImpact(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <button
                  onClick={handleLoadSaved}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <List size={18} />
                  <span>{loading ? 'Loading...' : 'Load Saved Bugs'}</span>
                </button>
              </div>

              {savedBugs && (
                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4">
                  <pre className="text-sm text-slate-800 dark:text-slate-200 whitespace-pre-wrap font-mono">
                    {savedBugs}
                  </pre>
                </div>
              )}
            </div>
          )}

          {activeTab === 'insights' && (
            <div>
              <h2 className="text-2xl font-semibold text-slate-900 dark:text-white mb-4">
                Analytics & Insights
              </h2>

              <div className="space-y-4 mb-6">
                <div>
                  <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                    Minimum Impact Score: {minImpact}
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={minImpact}
                    onChange={(e) => setMinImpact(parseInt(e.target.value))}
                    className="w-full"
                  />
                </div>

                <button
                  onClick={handleLoadInsights}
                  disabled={loading}
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  <BarChart3 size={18} />
                  <span>{loading ? 'Loading...' : 'Generate Insights'}</span>
                </button>
              </div>

              {insights && (
                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-4">
                  <pre className="text-sm text-slate-800 dark:text-slate-200 whitespace-pre-wrap font-mono">
                    {insights}
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

interface TabButtonProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}

function TabButton({ icon, label, active, onClick }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
        active
          ? 'bg-blue-600 text-white'
          : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700'
      }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}

export default App;

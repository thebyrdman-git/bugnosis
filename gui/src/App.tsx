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
  BarChart3,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Zap,
  Activity,
  Bug,
  Trophy,
  Medal,
  Target,
  Share2,
  Lock,
  Wifi,
  WifiOff,
  Moon,
  Sun
} from 'lucide-react';
import './App.css';

interface Stats {
  total_bugs: number;
  total_users: number;
  total_contributions: number;
  avg_impact: number;
}

interface Mission {
  id: string;
  title: string;
  xp: number;
  type: 'bug' | 'streak' | 'learning';
  progress: number;
  total: number;
}

// Helper component for Bug Cards
const BugCard = ({ bug }: { bug: any }) => {
  const isCritical = bug.impact_score >= 90;
  const isHigh = bug.impact_score >= 80 && !isCritical;
  
  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-slate-700 mb-4 transition-all hover:shadow-md">
      <div className="flex justify-between items-start">
        <div className="flex-1">
           <div className="flex items-center mb-1">
              <span className={`text-xs font-bold px-2 py-1 rounded uppercase mr-2 ${
                isCritical ? 'bg-red-100 text-red-700 border border-red-200' :
                isHigh ? 'bg-orange-100 text-orange-700 border border-orange-200' :
                'bg-emerald-100 text-emerald-700 border border-emerald-200'
              }`}>
                {isCritical ? 'Critical Impact' : isHigh ? 'High Impact' : 'Opportunity'}
              </span>
              <span className="text-xs text-slate-500 font-mono">{bug.repo}</span>
           </div>
           <h4 className="text-lg font-bold text-slate-800 dark:text-slate-200 mb-1">{bug.title}</h4>
           <div className="flex items-center text-sm text-slate-500 space-x-4 mt-2">
             <span className="flex items-center"><Target size={14} className="mr-1" /> Score: {bug.impact_score}/100</span>
             <span className="flex items-center"><Activity size={14} className="mr-1" /> Users: ~{bug.affected_users?.toLocaleString()}</span>
             <span className="capitalize">Severity: {bug.severity}</span>
           </div>
        </div>
        <div className="flex flex-col space-y-2 ml-4">
           <a 
             href={bug.url} 
             target="_blank" 
             rel="noreferrer"
             className="px-4 py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-700 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-300 rounded text-xs font-bold uppercase text-center transition-colors"
           >
             View Issue
           </a>
           <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded text-xs font-bold uppercase flex items-center justify-center transition-colors shadow-sm">
             <Zap size={14} className="mr-1" /> Fix Now
           </button>
        </div>
      </div>
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState('scan');
  const [selectedPlatform, setSelectedPlatform] = useState('github');
  const [repoInput, setRepoInput] = useState('');
  const [minImpact, setMinImpact] = useState(70);
  const [scanResult, setScanResult] = useState('');
  const [savedBugs, setSavedBugs] = useState<any[]>([]);
  const [savedBugsError, setSavedBugsError] = useState('');
  const [theme, setTheme] = useState('light');

  // ...

  useEffect(() => {
    // ... existing code ...
    
    // Load theme from local storage or default
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    if (savedTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }

    // Auto-load saved bugs if we start in Saved tab or just in background
    handleLoadSaved(); 
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    if (newTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  // ...

  const handleLoadSaved = async () => {
    setLoading(true);
    try {
      const result = await invoke<string>('get_saved_bugs', {
        minImpact: minImpact
      });
      try {
        const parsed = JSON.parse(result);
        if (Array.isArray(parsed)) {
             setSavedBugs(parsed);
             setSavedBugsError('');
        } else {
             // Handle case where it might return empty string or unexpected format
             setSavedBugs([]);
             if (result.trim()) setSavedBugsError(result); 
        }
      } catch (e) {
        // Fallback if JSON parse fails (e.g. if CLI wasn't updated yet)
        setSavedBugsError(result);
      }
    } catch (error) {
      setSavedBugsError(`Error: ${error}`);
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

  // Calculate status based on last scan (mocked for now based on result presence)
  const getStatus = () => {
    if (scanResult && scanResult.includes('No bugs found')) return 'secure';
    if (scanResult && scanResult.includes('high-impact bugs')) return 'risk';
    return 'unknown';
  };

  const status = getStatus();

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-slate-800 dark:text-slate-200 font-sans">
      {/* Top Bar (AV Header) */}
      <div className="bg-white dark:bg-slate-800 shadow-sm border-b border-gray-200 dark:border-slate-700 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <img src="/bug-logo.png" alt="Bugnosis" className="w-8 h-8" />
          <h1 className="text-xl font-bold text-emerald-600 dark:text-emerald-500 tracking-tight">BUGNOSIS <span className="font-normal text-slate-500 text-sm ml-1">Impact Engine</span></h1>
        </div>
        <div className="flex items-center space-x-6">
           <div className="flex items-center space-x-4 text-sm text-slate-500 font-mono">
              <span className="flex items-center"><Shield size={14} className="mr-1 text-emerald-500" /> Rank: {rankTitle}</span>
              <span className="flex items-center bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded"><Activity size={14} className="mr-1" /> Lvl {heroLevel}</span>
           </div>
           <button 
             onClick={toggleTheme}
             className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500 dark:text-slate-400 transition-colors"
             title={theme === 'light' ? 'Switch to Dark Mode' : 'Switch to Light Mode'}
           >
             {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
           </button>
        </div>
      </div>

      <div className="flex h-[calc(100vh-64px)]">
        {/* Sidebar Navigation */}
        <div className="w-64 bg-white dark:bg-slate-800 border-r border-gray-200 dark:border-slate-700 flex flex-col">
          <nav className="flex-1 p-4 space-y-2">
            <NavButton 
              icon={<Shield size={20} />} 
              label="Scanner Dashboard" 
              active={activeTab === 'scan'} 
              onClick={() => setActiveTab('scan')} 
            />
            <NavButton 
              icon={<Trophy size={20} />} 
              label="Hero Profile" 
              active={activeTab === 'profile'} 
              onClick={() => setActiveTab('profile')} 
            />
            <NavButton 
              icon={<Eye size={20} />} 
              label="Watch List" 
              active={activeTab === 'watch'} 
              onClick={() => setActiveTab('watch')} 
            />
            <NavButton 
              icon={<Bug size={20} />} 
              label="Saved Opportunities" 
              active={activeTab === 'saved'} 
              onClick={() => setActiveTab('saved')} 
            />
          </nav>
          <div className="p-4 border-t border-gray-200 dark:border-slate-700">
            <div className={`rounded p-3 border ${
              isOnline 
                ? 'bg-slate-50 dark:bg-slate-700/20 border-slate-200 dark:border-slate-600' 
                : 'bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800'
            }`}>
              <div className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">System Status</div>
              <div className={`flex items-center font-bold text-sm ${
                isOnline ? 'text-emerald-600 dark:text-emerald-500' : 'text-orange-600 dark:text-orange-500'
              }`}>
                {isOnline ? <Zap size={14} className="mr-2" /> : <WifiOff size={14} className="mr-2" />}
                {isOnline ? 'ENGINE ONLINE' : 'OFFLINE MODE'}
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 p-8 overflow-auto">
          
          {activeTab === 'scan' && (
            <div className="space-y-6">
              {/* Big Status Banner */}
              <div className={`rounded-lg p-8 text-center border-2 shadow-sm transition-colors ${
                status === 'secure' ? 'bg-emerald-50 border-emerald-200' :
                status === 'risk' ? 'bg-orange-50 border-orange-200' :
                'bg-slate-50 border-slate-200'
              }`}>
                {status === 'secure' ? (
                  <ShieldCheck size={64} className="mx-auto text-emerald-600 mb-4" />
                ) : status === 'risk' ? (
                  <ShieldAlert size={64} className="mx-auto text-orange-600 mb-4" />
                ) : (
                  <Search size={64} className="mx-auto text-slate-400 mb-4" />
                )}
                
                <h2 className={`text-3xl font-bold mb-2 ${
                  status === 'secure' ? 'text-emerald-700' :
                  status === 'risk' ? 'text-orange-700' :
                  'text-slate-700'
                }`}>
                  {status === 'secure' ? 'No High-Impact Bugs Found' :
                   status === 'risk' ? 'Impact Opportunities Detected' :
                   'Ready to Scan'}
                </h2>
                <p className="text-slate-600 max-w-lg mx-auto font-medium">
                  {status === 'secure' ? 'This repository appears healthy. No critical user-facing issues found.' :
                   status === 'risk' ? 'Several high-impact bugs require attention. Review the list below.' :
                   'Select a target platform and repository to begin impact assessment.'}
                </p>
              </div>

              {/* Scan Controls */}
              <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700 p-6">
                <h3 className="text-lg font-bold mb-4 flex items-center text-slate-700 dark:text-slate-200">
                  <Activity size={20} className="mr-2 text-emerald-600" />
                  Smart Search
                </h3>
                
                <div className="grid grid-cols-12 gap-4 mb-4">
                  <div className="col-span-9">
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Search Topic / Project</label>
                    <div className="relative">
                      <input
                        type="text"
                        value={repoInput}
                        onChange={(e) => setRepoInput(e.target.value)}
                        placeholder="E.g. 'Firefox', 'React', 'Linux Kernel', 'GitLab Runner'..."
                        className="w-full pl-10 pr-3 py-3 bg-gray-50 border border-gray-300 rounded focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all font-medium text-lg"
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                      />
                      <Search size={20} className="absolute left-3 top-3.5 text-slate-400" />
                    </div>
                  </div>
                  <div className="col-span-3">
                    <label className="block text-xs font-bold text-slate-500 uppercase mb-1">Impact Threshold ({minImpact})</label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      value={minImpact}
                      onChange={(e) => setMinImpact(parseInt(e.target.value))}
                      className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-600 mt-4"
                    />
                  </div>
                </div>

                <button
                  onClick={handleSearch}
                  disabled={loading}
                  className={`w-full py-4 rounded font-bold text-lg shadow-md transition-all transform hover:scale-[1.01] flex items-center justify-center uppercase tracking-wider ${
                    loading 
                      ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                      : 'bg-gradient-to-r from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white'
                  }`}
                >
                  {loading ? (
                    <>Scanning Ecosystem...</>
                  ) : (
                    <><Zap size={20} className="mr-2" /> Find High-Impact Bugs</>
                  )}
                </button>
              </div>

              {/* Results Terminal */}
              {scanResult && (
                <div className="bg-slate-900 rounded-lg p-0 shadow-lg overflow-hidden border border-slate-700">
                  <div className="bg-slate-800 px-4 py-2 flex items-center justify-between border-b border-slate-700">
                     <span className="text-xs font-mono text-slate-400">SCAN RESULTS</span>
                     <div className="flex space-x-1">
                       <div className="w-3 h-3 rounded-full bg-slate-600"></div>
                       <div className="w-3 h-3 rounded-full bg-slate-600"></div>
                     </div>
                  </div>
                  <div className="p-4 font-mono text-sm overflow-x-auto text-slate-300">
                    <pre>{scanResult}</pre>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'watch' && (
            <div className="space-y-6">
               <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Watch List Monitor</h2>
                  <button
                    onClick={handleScanWatched}
                    disabled={loading}
                    className="px-4 py-2 bg-emerald-600 text-white rounded font-bold text-sm uppercase shadow hover:bg-emerald-700 transition-colors flex items-center"
                  >
                    <Play size={16} className="mr-2" /> Scan All Targets
                  </button>
               </div>

               <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700 overflow-hidden">
                 <div className="p-4 bg-gray-50 dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700 flex gap-2">
                    <input
                      type="text"
                      value={repoInput}
                      onChange={(e) => setRepoInput(e.target.value)}
                      placeholder="Add new target (owner/repo)..."
                      className="flex-1 px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-emerald-500 font-mono text-sm"
                    />
                    <button 
                      onClick={handleAddWatch}
                      className="px-4 py-2 bg-slate-800 text-white rounded font-bold uppercase text-xs hover:bg-slate-700"
                    >
                      <Plus size={14} className="inline mr-1" /> Add Target
                    </button>
                 </div>
                 <div className="divide-y divide-gray-100 dark:divide-slate-700">
                    {watchedRepos.length === 0 ? (
                      <div className="p-8 text-center text-slate-500 italic">No repositories in watch list.</div>
                    ) : (
                      watchedRepos.map((repo, idx) => (
                        <div key={idx} className="p-4 flex items-center justify-between hover:bg-gray-50 dark:hover:bg-slate-700/50 transition-colors">
                          <div className="flex items-center">
                            <Eye size={18} className="text-slate-400 mr-3" />
                            <span className="font-medium font-mono text-sm">{repo}</span>
                          </div>
                          <span className="text-xs font-bold text-emerald-600 bg-emerald-50 border border-emerald-100 px-2 py-1 rounded uppercase">Monitoring</span>
                        </div>
                      ))
                    )}
                 </div>
               </div>
               
               {scanResult && (
                  <div className="bg-slate-900 rounded-lg p-4 shadow-lg font-mono text-sm overflow-x-auto text-slate-300 border border-slate-700">
                    <pre>{scanResult}</pre>
                  </div>
                )}
            </div>
          )}
          

          {activeTab === 'saved' && (
             <div className="space-y-6">
                <div className="flex items-center justify-between mb-6">
                   <div>
                      <h2 className="text-2xl font-bold text-slate-800 dark:text-white">Saved Opportunities</h2>
                      <p className="text-sm text-slate-500">Tracked bugs with high potential impact.</p>
                   </div>
                   <button
                      onClick={handleLoadSaved}
                      disabled={loading}
                      className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded font-bold text-sm uppercase transition-colors shadow-sm"
                    >
                      {loading ? 'Refreshing...' : 'Refresh List'}
                    </button>
                </div>

                <div className="min-h-[300px]">
                    {savedBugsError && (
                       <div className="bg-orange-50 border border-orange-200 text-orange-800 px-4 py-3 rounded mb-4">
                         {savedBugsError}
                       </div>
                    )}
                    
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-12 text-slate-400">
                           <Activity className="animate-spin mb-2" size={32} />
                           <p>Loading saved opportunities...</p>
                        </div>
                    ) : savedBugs.length > 0 ? (
                        <div className="grid grid-cols-1 gap-4">
                           {savedBugs.map((bug, idx) => (
                              <BugCard key={`${bug.repo}-${bug.issue_number}-${idx}`} bug={bug} />
                           ))}
                        </div>
                    ) : (
                      <div className="bg-white dark:bg-slate-800 rounded-lg p-12 text-center border border-gray-200 dark:border-slate-700">
                         <Shield size={48} className="mx-auto text-slate-300 mb-4" />
                         <h3 className="text-lg font-bold text-slate-600 dark:text-slate-400">No Opportunities Saved</h3>
                         <p className="text-slate-500">Scan repositories and use the --save flag to build your list.</p>
                      </div>
                    )}
                </div>
             </div>
          )}

          
          {activeTab === 'profile' && (
             <div className="space-y-6">
                {/* Hero Header */}
                <div className="bg-gradient-to-r from-slate-800 to-slate-900 rounded-lg p-8 text-white shadow-lg relative overflow-hidden">
                   <div className="relative z-10 flex items-center">
                      <div className="w-24 h-24 rounded-full bg-emerald-500 flex items-center justify-center text-4xl font-bold shadow-inner border-4 border-slate-700">
                         {heroLevel}
                      </div>
                      <div className="ml-6">
                         <h2 className="text-3xl font-bold mb-1">{rankTitle}</h2>
                         <p className="text-slate-400 mb-4">Impact Hunter Class</p>
                         
                         {/* XP Bar */}
                         <div className="w-96 bg-slate-700 rounded-full h-4 mb-2">
                            <div 
                              className="bg-emerald-500 h-4 rounded-full transition-all duration-1000" 
                              style={{ width: `${(currentXP / nextLevelXP) * 100}%` }}
                            ></div>
                         </div>
                         <div className="flex justify-between w-96 text-xs text-slate-400">
                            <span>{currentXP} XP</span>
                            <span>{nextLevelXP} XP to Lvl {heroLevel + 1}</span>
                         </div>
                      </div>
                   </div>
                   {/* Background decoration */}
                   <div className="absolute right-0 top-0 opacity-10">
                      <Bug size={300} />
                   </div>
                </div>

                <div className="grid grid-cols-2 gap-6">
                   {/* Missions */}
                   <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700 p-6">
                      <h3 className="text-lg font-bold mb-4 flex items-center">
                         <Target size={20} className="mr-2 text-emerald-600" />
                         Mission Control
                      </h3>
                      <div className="space-y-4">
                         <div className="p-4 border border-emerald-200 bg-emerald-50 dark:bg-emerald-900/10 rounded-lg">
                            <div className="flex justify-between items-start mb-2">
                               <h4 className="font-bold text-slate-800 dark:text-white">First Blood</h4>
                               <span className="text-xs font-bold bg-emerald-200 text-emerald-800 px-2 py-1 rounded">+500 XP</span>
                            </div>
                            <p className="text-sm text-slate-600 dark:text-slate-400 mb-3">Fix your first high-impact bug.</p>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                               <div className="bg-emerald-500 h-2 rounded-full" style={{ width: '0%' }}></div>
                            </div>
                         </div>
                         
                         <div className="p-4 border border-gray-200 rounded-lg opacity-60">
                            <div className="flex justify-between items-start mb-2">
                               <h4 className="font-bold text-slate-800 dark:text-white">Python Charmer</h4>
                               <span className="text-xs font-bold bg-slate-200 text-slate-800 px-2 py-1 rounded">+1000 XP</span>
                            </div>
                            <p className="text-sm text-slate-600 dark:text-slate-400">Contribute to 3 Python repositories.</p>
                         </div>
                         
                         <button className="w-full py-2 mt-2 text-sm text-emerald-600 font-medium hover:text-emerald-700">
                            View All Missions →
                         </button>
                      </div>
                   </div>

                   {/* Achievements */}
                   <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-700 p-6">
                      <h3 className="text-lg font-bold mb-4 flex items-center">
                         <Medal size={20} className="mr-2 text-orange-500" />
                         Trophy Case
                      </h3>
                      <div className="grid grid-cols-3 gap-4">
                         <div className="aspect-square rounded-lg bg-gray-100 dark:bg-slate-700 flex flex-col items-center justify-center p-2 text-center opacity-50">
                            <Lock size={24} className="mb-2 text-slate-400" />
                            <span className="text-xs font-bold text-slate-500">Boss Slayer</span>
                         </div>
                         <div className="aspect-square rounded-lg bg-gray-100 dark:bg-slate-700 flex flex-col items-center justify-center p-2 text-center opacity-50">
                            <Lock size={24} className="mb-2 text-slate-400" />
                            <span className="text-xs font-bold text-slate-500">Guardian</span>
                         </div>
                         <div className="aspect-square rounded-lg bg-gray-100 dark:bg-slate-700 flex flex-col items-center justify-center p-2 text-center opacity-50">
                            <Lock size={24} className="mb-2 text-slate-400" />
                            <span className="text-xs font-bold text-slate-500">Contributor</span>
                         </div>
                      </div>
                   </div>
                </div>
                
                {/* Share */}
                <div className="flex justify-end">
                   <button className="flex items-center space-x-2 text-slate-500 hover:text-emerald-600 transition-colors">
                      <Share2 size={18} />
                      <span>Share Hero Profile</span>
                   </button>
                </div>
             </div>
          )}

        </div>
      </div>
    </div>
  );
}

function NavButton({ icon, label, active, onClick }: { icon: any, label: string, active: boolean, onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg font-medium transition-colors text-left ${
        active
          ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-400'
          : 'text-slate-600 dark:text-slate-400 hover:bg-gray-50 dark:hover:bg-slate-700'
      }`}
    >
      {icon}
      <span>{label}</span>
    </button>
  );
}

export default App;

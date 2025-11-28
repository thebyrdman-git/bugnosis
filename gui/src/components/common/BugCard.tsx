import React from 'react';
import { Zap, Target, Activity } from 'lucide-react';
import { Bug } from '../../types';

interface BugCardProps {
  bug: Bug;
}

export const BugCard: React.FC<BugCardProps> = ({ bug }) => {
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


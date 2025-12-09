import React, { useState, useEffect } from 'react';
import { api } from './src/services/api';
import { User, ImageTask, Annotation, UserStats, UnpaidUser } from './src/types';
import { 
  LogOut, 
  CheckSquare, 
  FileUp, 
} from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

// ===== Login Component =====
const LoginScreen = ({ onLogin }: { onLogin: (user: User) => void }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const user = await api.login(username, password);
      onLogin(user);
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
      <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md">
        <h1 className="text-2xl font-bold text-center text-slate-800 mb-6">CrowdLabel Login</h1>
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-slate-600 mb-1">Username</label>
            <input className="w-full p-3 border rounded-lg" value={username} onChange={e=>setUsername(e.target.value)} required />
          </div>
          <div>
            <label className="block text-sm font-bold text-slate-600 mb-1">Password</label>
            <input className="w-full p-3 border rounded-lg" type="password" value={password} onChange={e=>setPassword(e.target.value)} required />
          </div>
          {error && <div className="text-red-500 text-sm">{error}</div>}
          <button disabled={loading} className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700">
            {loading ? 'Logging in...' : 'Sign In'}
          </button>
        </form>
      </div>
    </div>
  );
};

// ===== Annotator Dashboard =====
const AnnotatorDashboard = ({ onLogout }: { user: User, onLogout: () => void }) => {
  const [stats, setStats] = useState<UserStats | null>(null);
  const [task, setTask] = useState<ImageTask | null>(null);
  const [history, setHistory] = useState<Annotation[]>([]);
  const [loading, setLoading] = useState(false);

  const refresh = async () => {
    const [s, t, h] = await Promise.all([api.getStats(), api.getAvailableTask(), api.getHistory()]);
    setStats(s);
    setTask(t);
    setHistory(h);
  };

  useEffect(() => { refresh(); }, []);

  const handleSubmit = async (label: string) => {
    if (!task) return;
    setLoading(true);
    try {
      await api.submitAnnotation(task.id, label);
      await refresh();
    } catch (e: any) {
      const message = e?.message || 'Error submitting annotation';
      alert(message);
    } 
    finally { setLoading(false); }
  };

  if (!stats) return <div>Loading...</div>;

  // check if task is valid
  const hasTask = task && Array.isArray(task.options_list) && task.options_list.length > 0;

  // calculate stats for pie chart
  const pendingCount = history.filter(h => h.is_correct === null).length;
  const wrongCount = stats.totalAnnotated - stats.correctCount - pendingCount;
  
  const pieData = [
    { name: 'Correct', value: stats.correctCount, color: '#10b981' },
    { name: 'Wrong', value: wrongCount, color: '#ef4444' },
    { name: 'Pending', value: pendingCount, color: '#f59e0b' }
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white border-b p-4 flex justify-between items-center">
        <h1 className="font-bold text-xl flex items-center gap-2"><CheckSquare/> Workspace</h1>
        <div className="flex gap-6 items-center">
          <div className="text-right">
            <div className="text-xs text-slate-400">PENDING</div>
            <div className="font-mono font-bold text-amber-600">${stats.pendingBalance.toFixed(2)}</div>
          </div>
          <div className="text-right">
            <div className="text-xs text-slate-400">ACCURACY</div>
            <div className={`font-mono font-bold ${stats.accuracy < 0.7 ? 'text-red-500' : 'text-emerald-600'}`}>
              {(stats.accuracy * 100).toFixed(1)}%
            </div>
          </div>
          <button onClick={onLogout}><LogOut className="text-slate-400 hover:text-red-500"/></button>
        </div>
      </header>
      
      <main className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6 max-w-7xl mx-auto">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border">
            <h2 className="font-bold mb-4">Current Task {hasTask && task && <span className="bg-emerald-100 text-emerald-800 text-xs px-2 py-1 rounded ml-2">${task.bounty}</span>}</h2>
            {hasTask && task ? (
              <div className="space-y-4">
                <img src={task.image_url} alt="Task" className="w-full max-h-[400px] object-contain bg-slate-100 rounded" />
                <div className="grid grid-cols-4 gap-4">
                  {task.options_list.map(opt => (
                    <button key={opt} onClick={() => handleSubmit(opt)} disabled={loading}
                      className="py-3 border-2 rounded-lg font-bold hover:border-blue-500 hover:text-blue-600">
                      {opt}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-slate-400">No tasks available.</div>
            )}
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border h-64">
             <h3 className="font-bold mb-2">Stats</h3>
             <ResponsiveContainer width="100%" height="100%">
               <PieChart>
                 <Pie data={pieData} innerRadius={40} outerRadius={70} dataKey="value">
                   {pieData.map((e,i) => <Cell key={i} fill={e.color} />)}
                 </Pie>
                 <Tooltip />
               </PieChart>
             </ResponsiveContainer>
          </div>
          <div className="bg-white p-6 rounded-xl shadow-sm border h-[400px] overflow-y-auto">
             <h3 className="font-bold mb-4">History</h3>
             {history.map(h => (
               <div key={h.id} className="flex justify-between border-b py-2 text-sm">
                 <span>Image #{h.image} ({h.submitted_label})</span>
                 {h.is_correct === null ? <span className="text-amber-500 font-bold">Pending</span> : 
                  h.is_correct ? <span className="text-emerald-500 font-bold">Paid</span> : 
                  <span className="text-red-500 font-bold">Rejected</span>}
               </div>
             ))}
          </div>
        </div>
      </main>
    </div>
  );
};

// ===== Admin Dashboard =====
const AdminDashboard = ({ onLogout }: { user: User, onLogout: () => void }) => {
  const [tab, setTab] = useState<'reviews'|'payroll'|'tasks'>('reviews');
  const [reviews, setReviews] = useState<ImageTask[]>([]);
  const [unpaid, setUnpaid] = useState<UnpaidUser[]>([]);
  const [activeTasks, setActiveTasks] = useState<ImageTask[]>([]);
  
  // task form state
  const [url, setUrl] = useState('');
  const [cats, setCats] = useState('Cat, Dog, Bird');
  const [bounty, setBounty] = useState(0.5);

  const refresh = async () => {
    const [r, u, a] = await Promise.all([api.getReviewQueue(), api.getUnpaidUsers(), api.getAllActiveTasks()]);
    setReviews(r); setUnpaid(u); setActiveTasks(a);
  };
  useEffect(() => { refresh(); }, []);

  const handleResolve = async (id: number, label: string) => {
    try {
      await api.resolveConflict(id, label);
      await refresh();
    } catch (e: any) {
      alert(e?.message || 'Error resolving conflict');
    }
  };

  const handlePayroll = async () => {
    try {
      const res = await api.runPayroll();
      alert(`Paid out: $${res.total.toFixed(2)}`);
      await refresh();
    } catch (e: any) {
      alert(e?.message || 'Error processing payroll');
    }
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.addTask(url, cats, bounty);
      setUrl('');
      await refresh();
      alert('Task Added');
    } catch (e: any) {
      alert(e?.message || 'Error adding task');
    }
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      const r = new FileReader();
      r.onload = () => setUrl(r.result as string);
      r.readAsDataURL(f);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50">
       <header className="bg-slate-900 text-white p-4 flex justify-between items-center">
         <h1 className="font-bold text-xl">Admin Console</h1>
         <button onClick={onLogout}><LogOut size={20} /></button>
       </header>
       <main className="p-6 max-w-7xl mx-auto">
         <div className="flex gap-4 mb-6">
           {['reviews', 'payroll', 'tasks'].map(t => (
             <button key={t} onClick={() => setTab(t as any)} 
              className={`px-4 py-2 rounded capitalize font-bold ${tab===t ? 'bg-white shadow text-blue-600' : 'text-slate-500'}`}>
               {t}
             </button>
           ))}
         </div>

         {tab === 'reviews' && (
           <div className="grid grid-cols-2 gap-6">
             {reviews.map(r => (
               <div key={r.id} className="bg-white p-4 rounded shadow">
                 <img src={r.image_url} className="h-40 w-full object-cover rounded mb-4"/>
                 <h4 className="font-bold text-red-500 mb-2">CONFLICT DETECTED</h4>
                 <div className="flex gap-2">
                   {r.options_list.map(opt => (
                     <button key={opt} onClick={() => handleResolve(r.id, opt)} className="bg-slate-100 px-3 py-1 rounded hover:bg-emerald-500 hover:text-white">
                       {opt} (Set Truth)
                     </button>
                   ))}
                 </div>
               </div>
             ))}
             {reviews.length === 0 && <div className="text-slate-400">No conflicts.</div>}
           </div>
         )}

         {tab === 'payroll' && (
           <div className="bg-white p-6 rounded shadow">
             <div className="flex justify-between mb-4">
               <h2 className="font-bold text-xl">Pending Payments</h2>
               <button onClick={handlePayroll} disabled={unpaid.length===0} className="bg-emerald-600 text-white px-4 py-2 rounded font-bold disabled:opacity-50">
                 Settle All
               </button>
             </div>
             {unpaid.map(u => (
               <div key={u.userId} className="flex justify-between border-b py-3">
                 <span>{u.username} (ID: {u.userId})</span>
                 <span className="font-mono font-bold text-emerald-600">${u.amount}</span>
               </div>
             ))}
           </div>
         )}

         {tab === 'tasks' && (
           <div className="grid grid-cols-3 gap-6">
             <div className="col-span-1 bg-white p-6 rounded shadow h-fit">
               <h3 className="font-bold mb-4">Add Task</h3>
               <form onSubmit={handleAddTask} className="space-y-4">
                 <div className="flex gap-2">
                   <input value={url} onChange={e=>setUrl(e.target.value)} placeholder="Image URL" className="flex-1 border p-2 rounded" required />
                   <label className="bg-slate-200 p-2 rounded cursor-pointer"><FileUp size={16}/>
                    <input type="file" hidden onChange={handleFile} accept="image/*"/>
                   </label>
                 </div>
                 <input value={cats} onChange={e=>setCats(e.target.value)} placeholder="Cat, Dog" className="w-full border p-2 rounded" required />
                 <input type="number" step="0.01" value={bounty} onChange={e=>setBounty(parseFloat(e.target.value))} className="w-full border p-2 rounded" />
                 <button className="w-full bg-blue-600 text-white py-2 rounded">Add</button>
               </form>
             </div>
             <div className="col-span-2 grid grid-cols-2 gap-4">
                {activeTasks.map(t => (
                  <div key={t.id} className="bg-white p-2 rounded border flex gap-4">
                    <img src={t.image_url} className="w-20 h-20 object-cover rounded"/>
                    <div>
                      <div className="font-bold text-sm">ID: {t.id}</div>
                      <div className="text-xs text-slate-500">{t.assigned_count}/5 Assigned</div>
                      <div className="text-emerald-600 font-bold">${t.bounty}</div>
                    </div>
                  </div>
                ))}
             </div>
           </div>
         )}
       </main>
    </div>
  );
};

// ===== Main App =====
export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [init, setInit] = useState(false);

  // check if user is already logged in
  useEffect(() => {
    api.checkAuth().then(setUser).catch(() => {}).finally(() => setInit(true));
  }, []);

  const handleLogout = async () => {
    await api.logout();
    setUser(null);
  };

  if (!init) return <div>Loading...</div>;

  // show login screen if not logged in
  if (!user) return <LoginScreen onLogin={setUser} />;

  // show different dashboard based on role
  return user.role === 'admin' 
    ? <AdminDashboard user={user} onLogout={handleLogout} /> 
    : <AnnotatorDashboard user={user} onLogout={handleLogout} />;
}
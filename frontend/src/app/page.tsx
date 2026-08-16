import Link from 'next/link'

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center text-center p-4">
      <h1 className="text-5xl font-extrabold text-white mb-6 tracking-tight">Advocatus</h1>
      <p className="text-xl text-slate-400 max-w-2xl mb-10">
        Practice your legal reasoning against an AI Opposing Counsel powered by the Indian Contract Act, 1872.
      </p>
      <Link 
        href="/debate/new" 
        className="bg-indigo-600 hover:bg-indigo-700 text-white text-lg font-bold py-4 px-8 rounded-full shadow-lg shadow-indigo-500/30 transition-all hover:scale-105"
      >
        Start Practice Session
      </Link>
    </div>
  )
}

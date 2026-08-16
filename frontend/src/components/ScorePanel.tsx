export default function ScorePanel({ score }: { score: any }) {
  if (!score) return null;

  return (
    <div className="bg-slate-800 rounded-xl p-6 mt-6 border border-slate-700">
      <h2 className="text-2xl font-bold mb-4 text-white">Judge's Evaluation</h2>
      <p className="text-slate-300 mb-6 italic">"{score.overall_feedback}"</p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ScoreItem title="Issue Identification" data={score.issue_identification} />
        <ScoreItem title="Application of Law" data={score.application_of_law} />
        <ScoreItem title="Logical Structure" data={score.logical_structure} />
        <ScoreItem title="Rebuttal Responsiveness" data={score.rebuttal_responsiveness} />
      </div>
    </div>
  );
}

function ScoreItem({ title, data }: { title: string, data: any }) {
  return (
    <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
      <div className="flex justify-between items-center mb-2">
        <h3 className="font-semibold text-slate-200">{title}</h3>
        <span className="bg-indigo-600 text-white px-2 py-1 rounded text-sm font-bold">
          {data.score}/10
        </span>
      </div>
      <p className="text-sm text-slate-400">{data.feedback}</p>
    </div>
  );
}

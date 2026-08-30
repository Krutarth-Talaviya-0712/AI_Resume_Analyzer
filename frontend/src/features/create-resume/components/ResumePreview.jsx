import React, { useState } from 'react';
import html2pdf from 'html2pdf.js';
import { getTemplateById } from './templates';

const Preview = ({ 
  resumeData, 
  template, 
  onChangeTemplate, 
  handleInlineEdit, 
  sectionsOrder,
  updateArrayItem,
  updateSimpleArrayItem
}) => {
  const currentTemplate = (template && template.component) 
    ? template 
    : getTemplateById(template?.id || template?.template_id || template);
  const TemplateComponent = currentTemplate.component;
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDownloadPDF = async () => {
    if (isGenerating) return;
    setIsGenerating(true);

    const element = document.getElementById('resume-preview');
    if (!element) {
      setIsGenerating(false);
      return;
    }

    // Deep-clone the resume and attach it directly to <body> so html2pdf
    // captures the full A4 content without any parent transform or overflow clipping.
    const clone = element.cloneNode(true);
    clone.style.cssText = [
      'position:fixed',
      'top:-99999px',
      'left:0',
      'width:210mm',
      'min-height:297mm',
      'background:white',
      'z-index:-1',
      'visibility:hidden',
    ].join(';');
    document.body.appendChild(clone);

    // Let the browser paint the clone before capturing
    await new Promise(resolve => setTimeout(resolve, 400));

    try {
      const name = (resumeData?.name || 'Resume').trim().replace(/[^a-zA-Z0-9_-]/g, '_');
      const opt = {
        margin:      0,
        filename:    `${name}_Resume.pdf`,
        image:       { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true, logging: false, scrollX: 0, scrollY: 0 },
        jsPDF:       { unit: 'mm', format: 'a4', orientation: 'portrait' },
      };
      await html2pdf().set(opt).from(clone).save();
    } catch (err) {
      console.error('PDF generation failed:', err);
      alert('Could not generate PDF. Please try again.');
    } finally {
      document.body.removeChild(clone);
      setIsGenerating(false);
    }
  };

  return (
    <div className="w-full h-full flex flex-col bg-gray-200 relative overflow-hidden">
      
      {/* Toolbar */}
      <div className="flex justify-between items-center p-4 bg-white border-b shadow-sm z-10 shrink-0">
        <div className="flex items-center space-x-4">
           <button 
             onClick={onChangeTemplate} 
             className="text-sm font-medium text-blue-600 hover:text-blue-800 transition flex items-center gap-1"
             disabled={isGenerating}
           >
             <span>←</span> Change Template
           </button>
           <span className="text-sm text-gray-400">|</span>
           <span className="text-sm font-bold text-gray-700">{currentTemplate.name}</span>
        </div>
        
        <button 
          onClick={handleDownloadPDF} 
          disabled={isGenerating}
          className={`${isGenerating ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'} text-white px-5 py-2 rounded-lg shadow-md transition font-semibold flex items-center gap-2`}
        >
          {isGenerating ? (
            <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          ) : (
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          )}
          {isGenerating ? 'Processing...' : 'Download PDF'}
        </button>
      </div>

      {/* Preview Area */}
      <div className="flex-1 overflow-y-auto p-8 flex justify-center items-start scrollbar-thin scrollbar-thumb-gray-400">
        <div className="shadow-2xl bg-white w-full max-w-[210mm] min-h-[297mm] mx-auto overflow-hidden transform origin-top lg:scale-95 xl:scale-100 transition-transform">
           <div id="resume-preview" className="h-full w-full bg-white relative print-safe">
             <TemplateComponent 
                data={resumeData} 
                theme={currentTemplate.theme} 
                sectionsOrder={sectionsOrder}
                handleInlineEdit={handleInlineEdit}
                updateArrayItem={updateArrayItem}
                updateSimpleArrayItem={updateSimpleArrayItem}
             />
           </div>
        </div>
      </div>
    </div>
  );
};

export default Preview;

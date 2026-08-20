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
    const parentContainer = element.parentElement;

    // Apply print-safe state
    element.classList.add('downloading');
    if (parentContainer) parentContainer.classList.add('downloading-parent');

    // Wait for fonts and styles to settle
    await new Promise(resolve => setTimeout(resolve, 300));

    try {
      const fileName = `${(resumeData?.name || 'Resume').trim().replace(/[^a-zA-Z0-9_-]/g, '_')}_Resume.pdf`;
      const opt = {
        margin:       0,
        filename:     fileName,
        image:        { type: 'jpeg', quality: 0.98 },
        html2canvas:  { scale: 2, useCORS: true, logging: false },
        jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };

      await html2pdf().set(opt).from(element).save();
    } catch (error) {
      console.error('PDF export error:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      element.classList.remove('downloading');
      if (parentContainer) parentContainer.classList.remove('downloading-parent');
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

class ThoughtReportFormatter {
    constructor() {
        this.apiBase = 'http://localhost:5000/api';
        this.currentPages = [];
        this.currentPunctuationMarks = [];
        this.currentZoom = 100;
        this.currentPageIndex = 0;
        
        this.initElements();
        this.bindEvents();
        this.downloadBtn = null;
    }
    
    initElements() {
        this.textInput = document.getElementById('text-input');
        this.reporterName = document.getElementById('reporter-name');
        this.reportDate = document.getElementById('report-date');
        this.processBtn = document.getElementById('process-btn');
        this.clearBtn = document.getElementById('clear-btn');
        this.generateBtn = document.getElementById('generate-btn'); // 新增
        this.previewContainer = document.getElementById('preview-container');
        this.charCount = document.getElementById('char-count');
        this.pageEstimate = document.getElementById('page-estimate');
        this.pageInfo = document.getElementById('page-info');
        this.zoomIn = document.getElementById('zoom-in');
        this.zoomOut = document.getElementById('zoom-out');
        this.zoomLevelSpan = document.getElementById('zoom-level');
        this.loading = document.getElementById('loading');
        this.prevPageBtn = document.getElementById('prev-page');
        this.nextPageBtn = document.getElementById('next-page');
        this.downloadBtn = document.getElementById('download-pdf');
    }
    
    bindEvents() {
        this.textInput.addEventListener('input', () => this.updateStats());
        this.processBtn.addEventListener('click', () => this.processText());
        this.clearBtn.addEventListener('click', () => this.clearText());
        this.generateBtn.addEventListener('click', () => this.generateReport()); // 新增
        this.zoomIn.addEventListener('click', () => this.adjustZoom(10));
        this.zoomOut.addEventListener('click', () => this.adjustZoom(-10));
        this.prevPageBtn.addEventListener('click', () => this.goToPreviousPage());
        this.nextPageBtn.addEventListener('click', () => this.goToNextPage());
        this.downloadBtn.addEventListener('click', () => this.downloadPDF());
        
        // 键盘导航
        document.addEventListener('keydown', (e) => {
            if (this.currentPages.length > 0) {
                if (e.key === 'ArrowLeft') {
                    this.goToPreviousPage();
                } else if (e.key === 'ArrowRight') {
                    this.goToNextPage();
                }
            }
        });
        
        // 实时字符统计
        this.updateStats();
    }
    
    // 新增：生成范文功能
    async generateReport() {
        const userInput = this.textInput.value.trim();
        
        if (!userInput) {
            alert('请先输入您的个人情况或想法');
            return;
        }
        
        // 设置按钮为加载状态
        this.setGenerateButtonLoading(true);
        
        try {
            const response = await fetch(`${this.apiBase}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    user_input: userInput
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                // 将生成的内容替换到输入框
                this.textInput.value = data.generated_text;
                this.updateStats();
                
                // 自动执行格式化预览
                await this.processText();
                
                // 提示用户
                setTimeout(() => {
                    alert('范文生成成功！已自动进行格式化预览。');
                }, 500);
            } else {
                throw new Error(data.error || '生成失败');
            }
            
        } catch (error) {
            console.error('Generate Error:', error);
            alert(`生成范文失败: ${error.message}`);
        } finally {
            this.setGenerateButtonLoading(false);
        }
    }
    
    // 设置生成按钮的加载状态
    setGenerateButtonLoading(loading) {
        if (loading) {
            this.generateBtn.disabled = true;
            this.generateBtn.textContent = '生成中...';
        } else {
            this.generateBtn.disabled = false;
            this.generateBtn.textContent = '生成范文';
        }
    }
    
    // 更新下载按钮状态
    updateDownloadButton() {
        if (this.downloadBtn) {
            this.downloadBtn.disabled = this.currentPages.length === 0;
        }
    }
  
    updateStats() {
        const text = this.textInput.value;
        const charCount = text.length;
        const pageEstimate = Math.max(1, Math.ceil(charCount / 300));
        
        this.charCount.textContent = `字符数: ${charCount}`;
        this.pageEstimate.textContent = `预估页数: ${pageEstimate}`;
    }
    
    async processText() {
        const text = this.textInput.value.trim();
        const reporterName = this.reporterName.value.trim() || 'XXX';
        const reportDate = this.reportDate.value || '';
        
        if (!text) {
            alert('请输入文本内容');
            return;
        }
        
        this.showLoading(true);
        
        try {
            const response = await fetch(`${this.apiBase}/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    text: text,
                    reporter_name: reporterName,
                    report_date: reportDate
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.currentPages = data.pages;
                this.currentPunctuationMarks = data.punctuation_marks || [];
                this.currentPageIndex = 0;
                this.renderCurrentPage();
                this.updatePageInfo();
                this.updatePageButtons();
                this.updateDownloadButton();
            } else {
                throw new Error(data.error || '处理失败');
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert(`处理失败: ${error.message}`);
        } finally {
            this.showLoading(false);
        }
    }
    
    renderCurrentPage() {
        this.previewContainer.innerHTML = '';
        
        if (this.currentPages.length === 0) {
            this.previewContainer.innerHTML = `
                <div class="empty-preview">
                    <p>没有生成任何页面</p>
                </div>
            `;
            return;
        }
        
        const pageElement = this.createPageElement(
            this.currentPages[this.currentPageIndex], 
            this.currentPageIndex + 1, 
            this.currentPageIndex
        );
        this.previewContainer.appendChild(pageElement);
        
        this.applyZoom();
    }
    
    createPageElement(pageData, pageNumber, pageIndex) {
        const pageDiv = document.createElement('div');
        pageDiv.className = 'a4-page';
        
        const gridDiv = document.createElement('div');
        gridDiv.className = 'page-grid';
        
        // 获取当前页面的标点符号标记
        const punctuationMarks = this.currentPunctuationMarks[pageIndex] || [];
        
        // 创建20x20的网格
        for (let row = 0; row < 20; row++) {
            for (let col = 0; col < 20; col++) {
                const cell = document.createElement('div');
                cell.className = 'grid-cell';
                
                const char = pageData[row] && pageData[row][col] ? pageData[row][col] : '';
                const isPunctuationError = punctuationMarks[row] && punctuationMarks[row][col];
                
                if (char) {
                    cell.textContent = char;
                    cell.classList.add('filled');
                    
                    // 检查是否为行首标点符号错误
                    if (isPunctuationError) {
                        cell.classList.add('punctuation-error');
                        cell.title = '注意：行首不应使用标点符号';
                    }
                    // 添加其他特殊样式
                    else if (row === 0 && col >= 8 && col <= 11) {
                        cell.classList.add('title');
                    } else if (row === 1 && col <= 6) {
                        cell.classList.add('greeting');
                    } else if (char.includes('汇报人') || char.includes('年') || char.includes('月') || char.includes('日')) {
                        cell.classList.add('ending');
                    }
                }
                
                gridDiv.appendChild(cell);
            }
        }
        
        const pageNumberDiv = document.createElement('div');
        pageNumberDiv.className = 'page-number';
        pageNumberDiv.textContent = `第 ${pageNumber} 页`;
        
        pageDiv.appendChild(gridDiv);
        pageDiv.appendChild(pageNumberDiv);
        
        return pageDiv;
    }
    
    goToPreviousPage() {
        if (this.currentPageIndex > 0) {
            this.currentPageIndex--;
            this.renderCurrentPage();
            this.updatePageInfo();
            this.updatePageButtons();
        }
    }
    
    goToNextPage() {
        if (this.currentPageIndex < this.currentPages.length - 1) {
            this.currentPageIndex++;
            this.renderCurrentPage();
            this.updatePageInfo();
            this.updatePageButtons();
        }
    }
    
    updatePageInfo() {
        const totalPages = this.currentPages.length;
        const currentPage = totalPages > 0 ? this.currentPageIndex + 1 : 0;
        this.pageInfo.textContent = `第 ${currentPage} 页，共 ${totalPages} 页`;
    }
    
    updatePageButtons() {
        const totalPages = this.currentPages.length;
        
        if (totalPages <= 1) {
            this.prevPageBtn.disabled = true;
            this.nextPageBtn.disabled = true;
        } else {
            this.prevPageBtn.disabled = this.currentPageIndex === 0;
            this.nextPageBtn.disabled = this.currentPageIndex === totalPages - 1;
        }
    }
    
    adjustZoom(delta) {
        const newZoom = Math.max(50, Math.min(150, this.currentZoom + delta));
        if (newZoom !== this.currentZoom) {
            this.currentZoom = newZoom;
            this.zoomLevelSpan.textContent = `${this.currentZoom}%`;
            this.applyZoom();
        }
    }
    
    applyZoom() {
        const page = this.previewContainer.querySelector('.a4-page');
        if (page) {
            const scale = this.currentZoom / 100;
            page.style.transform = `scale(${scale})`;
        }
    }
    
    clearText() {
        this.textInput.value = '';
        this.reporterName.value = 'XXX';
        this.reportDate.value = '';
        this.currentPages = [];
        this.currentPunctuationMarks = [];
        this.currentPageIndex = 0;
        this.previewContainer.innerHTML = `
            <div class="empty-preview">
                <p>请在左侧输入文本并点击"格式化预览"</p>
            </div>
        `;
        this.updateStats();
        this.updatePageInfo();
        this.updatePageButtons();
        this.updateDownloadButton();
    }
    
    showLoading(show) {
        if (show) {
            this.loading.classList.remove('hidden');
        } else {
            this.loading.classList.add('hidden');
        }
    }
    
    // PDF下载功能
    async downloadPDF() {
        if (this.currentPages.length === 0) {
            alert('请先处理文本内容');
            return;
        }
        
        console.log('开始下载PDF...');
        
        // 显示下载进度
        this.showDownloadProgress();
        
        const { jsPDF } = window.jspdf;
        const pdf = new jsPDF({
            orientation: 'portrait',
            unit: 'mm',
            format: 'a4',
            compress: true
        });
        
        // 保存当前状态
        const originalPageIndex = this.currentPageIndex;
        
        try {
            // 为每一页单独截图
            for (let i = 0; i < this.currentPages.length; i++) {
                console.log(`处理第 ${i + 1} 页`);
                
                this.updateDownloadProgress((i / this.currentPages.length) * 100);
                
                // 切换到当前页
                this.currentPageIndex = i;
                this.renderCurrentPage();
                
                // 等待渲染完成
                await new Promise(resolve => setTimeout(resolve, 100));
                
                const pageElement = this.previewContainer.querySelector('.a4-page');
                if (pageElement) {
                    // 临时设置PDF导出模式
                    pageElement.classList.add('pdf-export-mode');
                    
                    const canvas = await html2canvas(pageElement, {
                        scale: 2,
                        useCORS: true,
                        allowTaint: true,
                        backgroundColor: '#ffffff',
                        width: pageElement.offsetWidth,
                        height: pageElement.offsetHeight
                    });
                    
                    // 移除PDF导出模式
                    pageElement.classList.remove('pdf-export-mode');
                    
                    const imgData = canvas.toDataURL('image/png');
                    
                    if (i > 0) {
                        pdf.addPage();
                    }
                    
                    // 计算图片尺寸以适应A4页面
                    const pdfWidth = 210; // A4宽度 mm
                    const pdfHeight = 297; // A4高度 mm
                    const imgWidth = pdfWidth - 20; // 留边距
                    const imgHeight = (canvas.height * imgWidth) / canvas.width;
                    
                    pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, Math.min(imgHeight, pdfHeight - 20));
                }
            }
            
            // 恢复原始页面
            this.currentPageIndex = originalPageIndex;
            this.renderCurrentPage();
            
            // 生成文件名
            const now = new Date();
            const dateStr = now.toISOString().split('T')[0];
            const reporterName = this.reporterName.value.trim() || 'XXX';
            const filename = `思想汇报_${reporterName}_${dateStr}.pdf`;
            
            // 保存PDF
            pdf.save(filename);
            
            this.hideDownloadProgress();
            
            setTimeout(() => {
                alert('PDF下载成功！');
            }, 500);
            
        } catch (error) {
            console.error('PDF生成失败:', error);
            alert(`PDF生成失败: ${error.message}`);
            this.hideDownloadProgress();
            
            // 恢复原始页面
            this.currentPageIndex = originalPageIndex;
            this.renderCurrentPage();
        }
    }
    
    showDownloadProgress() {
        const progressDiv = document.createElement('div');
        progressDiv.className = 'download-progress';
        progressDiv.id = 'download-progress';
        progressDiv.innerHTML = `
            <div>正在生成PDF...</div>
            <div class="progress-bar">
                <div class="progress-fill" id="progress-fill"></div>
            </div>
            <div id="progress-text">0%</div>
        `;
        document.body.appendChild(progressDiv);
    }
    
    updateDownloadProgress(percent) {
        const progressFill = document.getElementById('progress-fill');
        const progressText = document.getElementById('progress-text');
        if (progressFill && progressText) {
            progressFill.style.width = percent + '%';
            progressText.textContent = Math.round(percent) + '%';
        }
    }
    
    hideDownloadProgress() {
        const progressDiv = document.getElementById('download-progress');
        if (progressDiv) {
            progressDiv.remove();
        }
    }
  }
  
  // 初始化应用
  document.addEventListener('DOMContentLoaded', () => {
    new ThoughtReportFormatter();
  });
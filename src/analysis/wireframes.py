"""Six Power BI page blueprints, no fabricated charts or KPI values."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def generate():
    pages=[('01  Executive overview',['Population • Scored • High review • Unscored','Review workload by band','Sector share + denominators','Score distribution','Observed legal statuses']),('02  Sector intelligence',['SIC slicer • Company count • Scored denominator','Sector share ranking','Counts and score matrix','Crude vs age-standardised','Interval / sample-size table']),('03  Geographic intelligence',['Registered-office area slicer • Unknown retained','Area share ranking','Area counts + denominators','Sector mix within area','Company review queue']),('04  Filing signals & cohorts',['Accounts overdue • Confirmation overdue • Both','Deadline-days scatter','Delay-severity matrix','Current-register cohorts','Charges × observed status']),('05  Company investigation',['Company search • Score • Band • Eligibility','Score contribution waterfall','Profile + peer context','Deadlines + period end dates','Charges + verification link']),('06  Methodology & quality',['Reference date • Retrieval date • Input coverage','Source and proxy definition','Quality checks and exclusions','Policy + sensitivity table','Limitations and responsible use'])]
    fig,axes=plt.subplots(3,2,figsize=(18,15),facecolor='#f7f9fc')
    for ax,(title,labels) in zip(axes.flat,pages):
        ax.set_xlim(0,100);ax.set_ylim(0,100);ax.axis('off');ax.text(1,98,title,fontsize=16,weight='bold',color='#182c44',va='top')
        blocks=[(1,70,98,18),(1,39,47,26),(52,39,47,26),(1,8,47,26),(52,8,47,26)]
        for (x,y,w,h),label in zip(blocks,labels):
            ax.add_patch(Rectangle((x,y),w,h,facecolor='white',edgecolor='#b5c4d1',lw=1))
            import textwrap
            ax.text(x+w/2,y+h/2,'\n'.join(textwrap.wrap(label,34 if w>50 else 24)),ha='center',va='center',fontsize=12,color='#25354a')
    fig.suptitle('Power BI page wireframes • Build specification, not native report screenshots',fontsize=20,weight='bold',color='#182c44',y=.99)
    fig.tight_layout(rect=[.01,.01,.99,.97]);Path('dashboard/screenshots').mkdir(parents=True,exist_ok=True);fig.savefig('dashboard/screenshots/wireframes.png',dpi=120);plt.close(fig)
if __name__=='__main__':generate()

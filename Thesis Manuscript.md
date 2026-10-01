# Chapter 1: Introduction
## Background of the Study
The COVID-19 pandemic accelerated the adoption of online assessments across schools and certification programs, reshaping how examinations were conducted worldwide (Batool, Mumtaz, Ali, & Chughtai, 2018). Digital platforms offered flexibility and accessibility for remote learners, but they also introduced new challenges to academic integrity (Rettinger & Kramer, 2009; Holden, Norris, & Kuhlmeier, 2021). Without physical invigilators, online exams became vulnerable to misconduct, ranging from cheat sheets and messaging apps to unauthorized access of exam materials (Stuber, 2003; Rogers, 2006; Moten, Fitterer, Brazier, Leonard, & Brown, 2013). In response, researchers explored technological solutions such as webcam monitoring, gaze tracking, head pose estimation, and keystroke dynamics to detect suspicious behaviours (Hylton, Levy, & Dringus, 2016; Zhao & Ye, 2010; Bawarith, Basuhail, Fattouh, & Gamalel-Din, 2017; Matsumoto & Zelinsky, 2000; Dilini, Senaratne, Yasarathna, Warnajith, & Seneviratne, 2021; Danielsen & Gravdal, 2020). While platforms like Kryterion Online Proctoring integrated these tools, they often faced criticism for being costly, rigid, and negatively impacting user experience (Alshammari, 2020; Dimeo, 2017; Reddit, 2022). This highlights the need for systems that balance accuracy with usability, providing proctors actionable insights without overly restrictive measures (Binstein, 2015; Hu, Jing, Wu, & Pang, 2022). 
Holy Rosary College of Santa Rosa, Laguna (HRCSRL) reflects this broader trend. Like many institutions, it shifted to asynchronous online learning during the pandemic, later adopting hybrid approaches before returning to face-to-face classes in 2025–2026. Despite these transitions, online assessments remain part of its academic practice, particularly for quizzes and activity submissions. Interviews with faculty revealed that cheating through collusion, cheat sheets, and even unauthorized access to teacher workstations has been a persistent issue. This context makes HRCSRL an ideal setting for testing a suspicious exam behaviour detection system. With its computer laboratories and history of both online and traditional assessments, the institution provides a realistic environment to evaluate how such technology can strengthen academic integrity while maintaining usability for students and teachers.
## Statement of The Problem
The study has identified three key issues with current proctoring systems in education. First, existing systems rely on rigid detection mechanisms that often produce binary judgments. These systems typically classify behaviors as either acceptable or suspicious without considering the complexity of human actions. As a result, students may be unfairly flagged for minor or ambiguous movements, leading to false positives that undermine both the accuracy of the system and the overall user experience. Addressing this gap is crucial because false positives erode trust in proctoring technologies, discourage adoption by institutions, and create unnecessary stress for students who may feel penalized despite complying with exam rules.
Second, automated tools struggle to interpret nuanced test-taker behaviors. Current systems often lack the ability to differentiate between legitimate actions such as adjusting posture, looking away briefly, or typing irregularly, and actual cheating attempts. Without human intervention, these systems can misinterpret behaviors, resulting in unfair penalties, heightened student anxiety, and falsely flagged exam sessions. Covering this gap is essential because academic integrity solutions must balance vigilance with fairness. A system that fails to account for nuance risks alienating students, diminishing confidence in online assessments, and ultimately compromising the credibility of the institution’s evaluation process.
Lastly, a critical concern in the implementation of online proctoring systems is the requirement for software installation on either institution-owned or personal computers. These applications frequently demand high system permissions and incorporate lockdown browsers that restrict user control. Although such measures are intended to safeguard examination integrity, they simultaneously introduce vulnerabilities related to data privacy and the potential for unauthorized access to user information. In the context of increasing global emphasis on digital privacy, this requirement poses a significant challenge to user trust and acceptance. If students perceive proctoring systems as intrusive or compromising their personal data, resistance to adoption may arise, thereby undermining the effectiveness of online assessments and constraining the scalability of digital learning solutions. Addressing this issue is therefore essential to balance academic integrity with the protection of user rights.
## Objectives of the study
To address the rigidity of current detection systems, the study aims to develop a suspicious exam behaviour detection system that moves beyond binary judgments. Instead of relying on restrictive rules, the proposed system will integrate multiple detection features such as gaze tracking, head pose estimation and keystroke dynamics. By combining these inputs, the system will generate indicators of suspicious behaviour that can be interpreted by proctors. This layered approach reduces the likelihood of false positives and ensures that students are not unfairly penalized for minor or ambiguous actions. Ultimately, the system seeks to enhance accuracy while maintaining a smoother and less stressful user experience.
To address the lack of contextual understanding in automated proctoring tools, this study will develop a dataset specifically designed to describe suspicious exam behaviour. The dataset will serve as the foundation for exploratory model development, capturing irregular eye movements, head-pose changes, gaze durations, and recorded keyboard or browser events. By categorizing these session-level features, the dataset can help compare controlled normal and simulated suspicious conditions. In addition, the research will design, test, and integrate a gaze tracking system that tracks gaze direction, estimated in-screen gaze position, and gaze duration. This system will quantify visual-attention indicators and provide proctors with structured decision-making support. Presence of unauthorized objects is outside the implemented detection pipeline.
Finally, to mitigate privacy concerns associated with installed lockdown browsers, the study will develop a prototype web-app exam delivery service that integrates the detection system. Unlike traditional proctoring platforms that require intrusive installations, the web-based prototype will operate within a standard browser environment and will use account-based authentication together with browser-reported monitoring events. The implemented prototype focuses on face and eye landmark tracking, gaze estimation, head-pose analysis, and browser-level event reporting; facial recognition, liveness detection, object detection, and hand tracking are outside the implemented scope. By prioritizing usability and transparency, the system will provide a proof of concept that balances proctor assistance with respect for student data and institutional needs.
## Significance of the study
Cheating in online assessments continues to be a persistent problem despite the existence of current monitoring systems (Binstein, 2015). Many of these platforms rely heavily on automated algorithms that restrict student actions but often fail to account for nuanced behaviors, leading to issues of fairness, usability, and trust. This study is significant because it seeks to address these limitations by developing proctor assisting technologies that emphasize human judgment supported by data driven decision-making. Rather than replacing the role of proctors, the system is designed to provide them with actionable insights derived from quantifiable behavioral data, thereby strengthening their ability to detect and respond to misconduct assisting technologies that emphasize human judgment driven decision making. 
A key contribution to this project is its focus on transparency and accountability in online examinations. By enabling proctors to interpret data and make informed decisions, the system ensures that students understand that monitoring and interventions are guided by human oversight rather than solely by automated algorithms. This approach not only enhances trust between students and exam administrators but also promotes fairness by reducing the risk of false positives
and overly rigid restrictions. Furthermore, the system provides accountability mechanisms that allow institutions to document and justify proctor interventions whenever necessary. 
Lastly, the significance of this study lies in its potential to improve the integrity of online assessments while maintaining a user-friendly experience. By combining technological innovation with human judgment, the proposed system contributes to the ongoing effort to balance security, transparency, and ethical responsibility in digital education environments friendly experience.
The study aligns with the United Nations Sustainable Development Goals (SDGs),
particularly Goal 4: Quality Education, which mandates effective learning environments. The system contributes to this goal by restoring assessment of integrity through a non-invasive architecture. By ensuring valid educational outcomes, the system supports the imperative of maintaining high academic standards in a digital context. The study provides significant value to key educational stakeholders. Educational institutions benefit from a scalable method to safeguard academic credibility, while instructors gain a supportive tool that reduces monitoring fatigue and provides objective evidence of misconduct. Importantly, future researchers will have a baseline for creating a browser-based detection algorithm.
## Scope and Delimitations
This study focuses on the development of a Suspicious Exam Behaviour Detection
System (SEBDS) and the creation of a session-level dataset describing potentially suspicious exam behaviour. The implemented system monitors head pose, iris-based gaze position, gaze direction, gaze duration, and selected keyboard or browser events. It does not implement hand tracking, object detection, facial recognition, or liveness detection. These cues alone cannot confirm academic dishonesty; therefore, the system is designed to issue warnings and provide evidence for proctor review rather than accuse students of cheating.
The researchers will assess the system’s accuracy and performance through empirical experiments and on-site user testing within a controlled environment in the specific research locale. The findings may not be fully generalizable to different hardware configurations or uncontrolled settings. For the web application development, the scope is further delimited to the implementation of baseline data privacy safeguards, rather than advanced security architecture. Finally, the study acknowledges potential limitations regarding sample size, selection method, response bias, and equipment variables during testing that may influence the results. In addition to this, the scope of this study is also confined to the development and evaluation of a basis and thresholds of a Suspicious Exam Behaviour Detection System. 
The primary focus is on identifying behaviours that may correlate with cheating or academic misconduct in online examinations. These behaviours include irregular eye movements, unusual head poses, and atypical keypress or browser events that may suggest reliance on external resources. In the browser implementation, reported key events and focus-state changes are sent from the exam page; the system does not provide unrestricted OS-level monitoring in the web path. Given these limitations, and as noted in Garg and Goel (2023), it is difficult to conclusively determine cheating based solely on gaze or head-pose behavior. Such actions may occur naturally and not necessarily indicate misconduct. In recognition of this limitation, the system will not automatically treat these behaviours as proof of cheating. Instead, it generates warnings and session indicators for proctor review.
The study aims to deliver a functional prototype of the system, and along with it, the dataset created after the creation of the detection system. This is to evaluate its usability, effectiveness, and accuracy in the specified research locale. To achieve this, locale member trial runs and on site system testing will be employed as the primary methods of data collection. These instruments will provide insights into how system outputs and behavioral data correspond to actual test taking conduct, enabling evaluation of the system’s capacity to distinguish normal behavior from suspicious activity. Furthermore, the trial runs and system testing will allow assessors to examine the system’s transparency, fairness, and accuracy, as well as its non intrusiveness for students and practical usefulness for proctors and teachers in maintaining exam integrity.
Data collection will be limited to the duration of the study and the specific research locale identified by the proponents. The evaluation will be conducted under controlled conditions designed to simulate realistic exam environments. However, the findings may not be generalizable to other contexts, such as different hardware configurations, varied internet connectivity levels, or alternative institutional settings. The scope is therefore restricted to the immediate sample group and environment, acknowledging that broader application would require further testing and validation. The delimitations of the study include several constraints that may influence the outcomes. These include the relatively small sample size, the selection method of participants, and the potential for response bias in self-reported measures. Equipment variables, such as differences in webcams, microphones, or computing devices, may also affect detection of accuracy during on-site testing. Furthermore, there may be undetermined external factors not accounted for in this study that could influence results, such as environmental distractions or variations in student qualities and behaviours unrelated to cheating. 
While the system incorporates baseline safeguards for data privacy and security, these measures are limited to ensuring minimum compliance and operational requirements. The central focus of the project is the design and evaluation of the suspicious exam behaviour detection system, its thresholds and basis, dataset creation as well as a functional web app prototype as a proof of concept, rather than the development of advanced privacy or security frameworks. Issues such as long-term data storage, encryption standards, and institutional data governance policies fall outside the scope of this study and are acknowledged as areas for future research and refinement. The study evaluates the technical performance of the implemented computer vision algorithms in terms of detection accuracy and processing speed strictly within the research testing equipment, and results may vary based on these changes. 
The system’s performance will be examined using the available session-level dataset and reported with appropriate classification metrics. Precision is an important metric because false positives are costly in a proctor-assistance context. During inference, the classifier’s `predict()` output supplies the predicted class label, while the probability assigned to that returned class is recorded as the confidence level. Each detected behaviour is categorized in the event log and may receive a rule-based score, while the later Random Forest inference produces a separate class probability and prediction confidence. These outputs should be treated as decision-support indicators, not as standardized measures of misconduct likelihood.
## Research Framework
Figure 1. Research Framework Diagram
 
This study is anchored on a multi-phase research framework that guides the development, integration, and evaluation of a web-based online examination platform equipped with automated behavioural analysis. The framework is structured into seven interconnected modules, each representing a critical stage in the system’s lifecycle from model evaluation to deployment and acceptance.
## Model Evaluation
The initial phase focuses on evaluating the core components of the behavioural detection system: the MediaPipe facial-landmark pipeline, iris-based gaze estimation, head-pose processing, browser or keyboard event handling, and rule-based scoring. The study evaluates the selected pipeline as an integrated design, while comparisons with alternative CV algorithms are addressed through related literature and proposed as future work. These evaluations determine whether each detection modality contributes meaningfully to the behavioural indicators.
## Model Development and Scoring System
Following the evaluation, the available session data is transformed into heatmap-distribution and event-log features for exploratory model development. The current feature set is based on gaze-distribution measures, an 8x8 heatmap grid, violation-category counts, transitions, non-center time, and violation rate. The implemented scoring engine applies deterministic temporal and event rules; it does not use object-detection features. A separate Random Forest artifact provides session-level classification probabilities when the required artifacts are available.
## Web Application Development
Once the model has been properly developed and tested, it is then embedded into a secure web-based platform developed using Python Django, a Python-based web application development framework. The application will be used to create and take exams based on the role of the end user. This module prioritizes the development of a web application system tailored to academic settings, to integrate the suspicious behaviour detection system into online exam taking.
## Respondent Engagement and Usage
The system is designed for two primary user groups: Students and Teachers. Their feedback and usage patterns are essential for evaluating system usability and effectiveness.
## Testing and Evaluation
This phase involves empirical validation of the system through surveys, questionnaires, results evaluation, and usage performance testing. These activities provide quantitative insights into system performance.
## Ethical Considerations and Feedback
Ethical integrity is central to system deployment. This module addresses transparency and informed consents, user privacy, system performance enhancements feedback. This phase ensures alignment with institutional standards and user expectations.
## Documentation and Recommendations
The final module of the conceptual framework diagram encompasses the documentation and recommendations of the researchers for future development of the thesis topic. The documentation section encompasses: 
- System Architecture Records. Detailed diagrams and descriptions of the detection system and the web application frontend and backend will be recorded in detail.
- Algorithmic Specification. This will cover the clear explanation of the CV models, keypress tracking methods and scoring mechanics. Additionally, datasets and evaluation metrics, as well as calibration thresholds will be documented.
- Ethical Compliance Reports. Documents related to the informed consent procedures, privacy safeguards, and institution approvals will be archived for recordkeeping.
As for the recommendations, the following will be established for further development and evaluation of the thesis theme to ensure a clear and efficient roadmap. This may include:
- Technical Enhancements. This could relate to dataset expansion, future CV model recommendations, or expanded scope to the various behaviours and factors that lead to suspicious exam behaviour.
- User-focused Improvements. This could be the existing feedback and recommendations that are logged and archived during the documentation process. The following examples could be reconducting of user training for system familiarity, UI improvements and recommendations, and accessibility features to accommodate a larger group of users.
- Future Research Directions. The research group will document and transcribe any recommendations or improvements for the further integration and efficacy of the system. These can include encompassing current limitations that are possible in a future time due to factors such as technological advancements or new discoveries related to the topic of the study.
# Chapter 2: Related Literature Review
This chapter presents a synthesized review of literature on online assessment, academic integrity, and the effectiveness of artificial intelligence–based proctoring systems. The discussion traces the evolution from traditional paper based examinations to digital assessment environments, identifies emerging patterns of academic misconduct in online settings, and evaluates technological interventions intended to ensure fairness and authenticity during remote examinations.
## The Shift from Physical to Digital Assessment
Before the COVID 19 pandemic, traditional paper and pen examinations were widely regarded as reliable methods of student evaluation because their controlled, face to face nature enabled direct invigilation and reduced opportunities for academic dishonesty (Zhao et al., 2022; Forgas, 2021). The pandemic precipitated an unprecedented global transition to distance learning, affecting approximately 1.5 billion students worldwide (Zarzycka et al., 2021). This abrupt shift required rapid adoption of digital assessment platforms despite limited preparation time, with infrastructure readiness and faculty training often lagging behind need (Fagell, 2020; Valverde Berrocoso, 2020). Consequently, the central concern moved beyond content delivery toward maintaining validity and integrity in unmonitored or lightly supervised online examinations (Gamage et al., 2020).
## Evolving Patterns of Academic Misconduct in Online Settings
## Prevalence and Student Perceptions
Evidence indicates that online learning environments are associated with higher rates of academic dishonesty relative to traditional classroom settings. For example, self reported cheating rose from 29.9% in pre pandemic contexts to 44.7% after the widespread adoption of online assessments (Newton, 2023). Independent studies report similar patterns across diverse populations: approximately 60% of students in Pakistan engaged in online cheating and often obtained higher grades than in face to face assessments (Malik, 2023); 42.3% of college students reported cheating online compared with 28.3% in person (Liang et al., 2023). Perception studies also suggest that both faculty and students view online examinations as more vulnerable to misconduct than traditional formats (Harton et al., 2019).
## Drivers and Contemporary Methods of E Cheating
The shift to online modalities expanded perceived opportunities and lowered perceived risks, while stressors—such as fear of failure, pandemic related anxiety, and normalization of dishonest behavior in low supervision contexts—further motivated misconduct (Noorbehbahani, 2022; Carrasco, 2022). Moreover, technology broadened the repertoire of cheating methods beyond traditional aids; students now employ artificial intelligence tools, virtual machines, unauthorized collaboration, and other digital workarounds to evade standard security protocols (Chadaga, 2025; Janison, 2025).
## AI Based Proctoring and Computer Vision Technologies
## Performance Metrics and System Capabilities
In response to these challenges, institutions increasingly deploy artificial intelligence and computer vision (CV) to monitor behavior and protect assessment integrity. Multi camera systems significantly outperform single camera setups, achieving up to 95% accuracy in detecting both individual and collaborative cheating (Hu et al., 2024). Automated identity verification and liveness detection using deep learning reach recognition accuracies as high as 96.2%, thereby mitigating impersonation risk (Oravec, 2020). Even in low resource environments, browser based gaze tracking systems—requiring no specialized hardware—have achieved approximately 89.53% accuracy, indicating that effective monitoring can be accessible and scalable (Dilini et al., 2021).
## Cheating Detection Systems Using Computer Vision Algorithms
Recent advancements in computer vision (CV) and artificial intelligence (AI) have enabled the development of automated cheating detection systems capable of monitoring examinee behaviors during online assessments. These systems frequently integrate object detection, facial recognition, eye gaze tracking, and facial movement analysis to identify suspicious activities that may compromise examination integrity (Matsumoto & Zelinsky, 2000; Hu et al., 2024; Dilini et al., 2021).
In the study conducted by Hu et al. (2024), the researchers proposed a multi perspective automated monitoring system designed to identify cheating behaviors in online examinations. The system utilized three distinct camera viewpoints—overhead, horizontal, and facial—to provide a comprehensive representation of the examinee’s workspace and actions. Cheating behaviors were categorized into two groups: individual cheating, which involves the use of unauthorized tools by the examinee, and assisted cheating, wherein external individuals indirectly support the examinee during the test.
Figure 2. Gaze Positions
 

The study further noted that only gazes directed toward the center of the screen were considered “normal” eye positions. Any deviation from this central gaze pattern was treated as potentially irregular. Hu et al. emphasized that an effective automated invigilation system should integrate visual, acoustic, and physiological indicators, with camera based monitoring identified as the most intuitive and reliable approach. Three monitoring configurations were evaluated: single perspective, dual perspective, and multi perspective systems. Although the single perspective system offered lower cost and faster processing, it lacked sufficient evidence for reliable detection. The dual perspective system improved coverage but remained unable to capture peripheral behaviors. Ultimately, the multi perspective configuration demonstrated superior performance by enabling a full assessment of both the examinee and their surrounding environment.
To operationalize this system, Hu et al. implemented advanced deep learning models, including the Swin Transformer for gaze detection and Lightweight YOLOv5 CA with Group Fast Spatial Pyramid Pooling (GFSPP) for object detection. These models enabled the identification of unauthorized tools from multiple angles. A Backpropagation Neural Network was then used to weigh and classify extracted features, achieving an overall detection accuracy of 95%.
Figure 3. Neural Network Interpretations of Exam Behaviours and Tracked Environment Entities
  
Complementing this approach, Dilini et al. (2021) introduced a browser based eye gaze tracking system intended for online cheating detection. Their system implemented a nine point calibration procedure to establish user specific gaze boundaries and employed a One Class Support Vector Machine (OCSVM) to detect anomalous patterns. Because browser level monitoring does not require specialized hardware, this approach highlighted a scalable solution for remote examination monitoring. The system achieved an accuracy of 89.53%, underscoring the viability of lightweight behavioral analysis tools.
In another study, Oravec (2020) focused on preventing impersonation during online examinations using a deep learning–based facial recognition and liveness detection system. By employing a ResNet 50 architecture, the system attained an average identity verification accuracy of 96.2%, significantly reducing instances of impersonation. These findings highlight the essential role of identity authentication within AI enabled online proctoring frameworks.
## Ethical Considerations and User Experience
Despite promising technical performance, remote proctoring tools raise concerns related to user experience and well being. Students report heightened anxiety and discomfort attributable to surveillance features, which may negatively affect performance (Marano et al., 2023). Additionally, commercial systems have been criticized for false positives, usability issues, and technical malfunctions, which can undermine trust and perceived fairness (Foster & Layman, 2013; Hussein et al., 2020). These concerns underscore the need to balance integrity protection with student autonomy, privacy, and psychological safety.
## Related Literature Synthesis
## Rationale
Online assessment has matured into a space where integrity, usability, and ethics must be balanced and not by chasing perfect detection, but by supporting informed human judgment. A proctor-assistance tool paired with an exam delivery app, using a single-camera perspective to estimate gaze from eye and face orientation, fits that balance. It surfaces suspicious behaviours as data, not verdicts, and keeps proctors in the loop rather than replacing them. This approach acknowledges that academic integrity is a central concern in online assessment, as numerous studies highlight increased opportunities for misconduct in remote exams and the need for credible monitoring that preserves fairness and trust (Holden et al., 2021; Janke et al., 2021; Bilen & Matros, 2021; Gamage et al., 2020; Harton et al., 2019; Vellanki et al., 2023).
## Reframing System Roles: From Detection to Assistance
Cheating behaviors are often responses to stress and insufficient supervision (Jalilzadeh et al., 2024). While automated systems can detect anomalies, they may also produce false positives that contribute to test anxiety (Marano et al., 2023; Hussein et al., 2020). Accordingly, the present study positions its tool as a proctor assistance system that surfaces suspicious behaviors as interpretable data points for human review, rather than issuing definitive judgments, an approach consistent with human in the loop practices emphasized in the literature (Marano et al., 2023; Hussein et al., 2020; Jalilzadeh et al., 2024).
## Technological Approaches Informed by Evidence
Although multi perspective camera systems demonstrate high accuracy, they impose hardware and bandwidth burdens that may disadvantage certain students. In line with equity considerations and empirical performance baselines, this research adopts a single camera, browser based gaze estimation approach, reflecting evidence that such systems can reach high accuracy without specialized equipment (Dilini et al., 2021; Hussein et al., 2020). This choice balances feasibility and fairness while maintaining acceptable detection performance (Hu et al., 2024; Dilini et al., 2021).
## Ethical Positioning of Monitoring Systems
Overly intrusive surveillance may have counterproductive effects on student well being and autonomy (Oravec, 2022). To mitigate these risks, the proposed system avoids binary classifications (i.e., “cheating” vs. “not cheating”) and instead aggregates indicators, such as gaze frequency and duration, into a behavioral score that informs, rather than replaces, human decision making (Oravec, 2022; Marano et al., 2023).
## Integration into Broader Academic Integrity Frameworks
Technology is most effective when embedded within institutional cultures that promote academic honesty. Proctoring tools should complement, not replace, existing policies and honor codes (Vellanki et al., 2023). By offering transparency and interpretability, the system contributes to a layered integrity ecosystem that supports fairness and trust in digital education (Goff et al., 2020; Benson & Enstroem, 2023).
# Chapter 3: Methodology
## Preface
Prior to this study, various prototypes were already developed by the researchers, specifically the suspicious exam behavior detection system. The initial prototype does not follow the current thresholds and basis of the current study requiring changes and integration to a more comprehensive system. 
## Limitations of the Web App Prototype
Although the study developed a prototype web-based examination platform integrating the suspicious exam behaviour detection system, data gathering was conducted through controlled offline stand-in web application simulations, and additionally used a computer-installed software version of the detection system, rather than live deployment of the web application. This methodological choice was made to ensure consistency in testing conditions and to isolate the performance of the detection algorithms from external factors such as network latency, browser compatibility, and server load. By focusing on algorithmic evaluation, the researchers were able to measure detection accuracy, precision, and behavioral thresholds under standardized conditions. The prototype served primarily as a proof of concept to demonstrate integration feasibility, while full-scale usability testing through the web app is recommended for future research to validate system scalability and user experience in real-world environments.
## Research Design
This study adopts a quantitative design, using an experimental and literature-acquired knowledge to ensure a comprehensive evaluation of the proposed system. The design was chosen because it allows the proponents to integrate quantitative performance testing with related literature user feedback, thereby addressing both technical accuracy and human centred considerations.
The experimental evaluation focuses on assessing the selected computer-vision pipeline and keypress or browser-event strategies that form the core of the suspicious exam behaviour detection system. The pipeline uses MediaPipe facial landmarks, iris-based gaze estimation, head-pose processing, and deterministic behavioral scoring. Precision, recall, F1 scores, and confusion matrices are used where classification results are evaluated, while alternative model comparisons are addressed through related literature and future work.
Complementing this, using existing research related to this technology, the research will use to take into considerations what previous research have observed through qualitative means. This qualitative input is used to guide design modifications, ensuring that the system is not only technically sound but also aligned with user expectations. By incorporating perceptions of trust, transparency, and privacy, the study ensures that ethical considerations are embedded into the development process.
Together, these two approaches provide a balanced framework: the experimental evaluation validates the technical feasibility of the detection models, while the literature-related knowledge approach ensures that the system remains practical, acceptable, and ethically responsible in real academic settings.
## Research Locale
The project was conducted at Holy Rosary College of Santa Rosa, Laguna, a private educational institution that provides K–12 education. The institution is equipped with computer laboratories and is well prepared to administer online assessments to its students. With these resources, the institution provided an ideal environment for testing the project. This locale was selected for its accessibility, its population’s familiarity with online learning tools, and the presence of ICT focused classes and teaching staff.
## Software Methodology
Figure 4. Software Methodology
 
The software methodology implemented in this study is the KANBAN methodology, chosen for its flexibility, modularity, and suitability for iterative development. KANBAN was selected because the system being developed is an integrated processing unit composed of two main parts: the web based exam delivery tool and the suspicious behavior detection system. By breaking the project into these modular components, tasks can be performed in parallel and visualized effectively on a KANBAN board. This approach also allows proponents to distribute responsibilities among team members more efficiently, ensuring that development progresses in a structured yet adaptable manner.
Another reason for adopting KANBAN is its support for continuous iterative development. Since the web app system relies heavily on user experience and tester feedback, KANBAN provides the accessibility needed to reprioritize software modifications whenever new knowledge from related literature is found. This iterative cycle ensures that the system evolves thereby improving usability and effectiveness over time.
KANBAN also offers flexibility in task prioritization, which is essential given the mixed methods approach of this study. The methodology combines technical testing results with user feedback to guide decision making. As new requirements or issues emerge, tasks can be reprioritized on the KANBAN board, ensuring that the most critical modifications are addressed first.
The methodology emphasizes the importance of visualizing task workflow. The KANBAN board provides a clear representation of tasks categorized into stages such as “to do,” “backlog,” “in review,” “prioritized,” and “documentation.” This visualization enables the team to track progress modularly, monitor test results, and identify modifications based on user feedback. Examples include tracking the completion of standard operating procedures (SOPs), monitoring the outcomes of system testing, and documenting adjustments made during development. By maintaining this structured workflow, the team ensures transparency, accountability, and efficiency throughout the project lifecycle.  
Figure 5. KANBAN Visualization
## Population of the Study
The population of this study consists of selected members of Holy Rosary College of Santa Rosa, Laguna, specifically students and teachers who participated in the system testing. The sampling method employed was a convenience sampling approach with random selection, chosen for its practicality and accessibility within the research locale. This method allowed the researchers to gather participants who were readily available and familiar with ICT related tools and online platforms, while still ensuring diversity through random selection.
The locale sample consisted of 93 student participants from Grades 8 to 12, representing a range of academic levels and technological familiarity. This participant count is distinct from the 186 session-level observations in the dataset because participants could contribute more than one session. Two teacher participants also provided professional insight and feedback on system usability and proctoring effectiveness.
The combination of convenience and random sampling provided a balanced approach, leveraging accessibility while minimizing bias through random participant selection. This structure ensured that the data gathered was both relevant to the study’s objectives and representative of the typical users of the system within the institution.
## Data Gathering Tools and Procedures
User privacy, informed consent, and participant interests were carefully considered during the development of the fundamental aspects of the project. To address these concerns, the proponents conducted a trial run orientation as well as written informed data privacy consent forms encompassing the scope of use of the gathered personal data in the research. In addition, participants were asked what specific details they would like to be informed about when using the system, ensuring transparency and accountability throughout the research process. 
	During the initial development of the system and its algorithms. The study used the following hardware relevant to the study: 

Table 1. Hardware Specifications During Development
Hardware	Specification
Camera	UVC Camera – 1080p High Definition Camera
Monitor	2560x1440 Resolution 32-inch Monitor
Graphics Processing Unit	NVIDIA GeForce RTX 3060
RAM	32 GB

Table 2. Hardware Specifications During Locale Trial Runs
Hardware	Specification
Camera	UVC Camera – 1080p High Definition Camera
Monitor	2560x1440 Resolution 32-inch Monitor
Graphics Processing Unit	Intel(R) UHD Graphics 620
RAM	8 GB


Figure 6. Locale System Testing Setup
   
The experimental setup was established within the designated testing area of Holy Rosary College of Santa Rosa, Laguna. Each trial session utilized a 2020 Lenovo ThinkPad laptop connected to a 32 inch external monitor, providing a clear and standardized display environment for all participants. A 1080p 60 fps webcam was mounted above the monitor to capture facial orientation and gaze behavior in real time, ensuring high-resolution input for the computer vision modules.
To complement the primary camera feed, a smartphone mounted on a tripod was positioned at the back left side of the tester, recording the participant, desk, monitor, and surrounding area to provide contextual footage of the testing environment. Additionally, the screen activity of both the tester’s monitor and the researcher’s monitor was recorded throughout each session. This dual screen recording allowed synchronized observation of the participant’s exam interface and the system’s detection dashboard, enabling precise correlation between gaze behavior, system alerts, and real time events.
The combination of multiangle video capture and synchronized screen recording ensured comprehensive documentation of each trial, supporting both qualitative and quantitative analysis of the system’s performance under controlled conditions.


Figure 7. Exam Interface for Data Gathering
  
For the data gathering phase, the researchers utilized a separate test taking web application rather than the prototype web app system that integrates the eye-tracking and detection modules. This methodological decision was made to ensure stability and prevent compounded bug-fixing during the testing stage. Because the prototype was still under active development, combining exam delivery and detection functionalities could have introduced overlapping technical issues that might compromise data integrity and delay evaluation.
The use of a dedicated test taking platform allowed the researchers to isolate the behavioral data collection process from the detection system’s internal testing. This separation ensured that any anomalies encountered during trials could be attributed specifically to the detection algorithms rather than to the exam interface itself. It also provided a controlled environment for participants to complete assessments without interference from prototype debugging or integration errors.
Furthermore, this approach aligns with the primary and secondary objectives of the thesis: (1) to develop a functional suspicious exam behavior detection system, and (2) to generate a dataset derived from the system’s operation for use by future researchers. By employing a separate test taking system, the study maintained methodological clarity, allowing the detection system to be evaluated independently while ensuring that the resulting dataset accurately reflects behavioral patterns rather than software inconsistencies. This separation ultimately strengthened the reliability, validity, and future applicability of the research outcomes.
The trial test-taking web application used for data gathering was developed in Google AI Studio as a lightweight platform for administering examinations. It provided manual question entry and AI-assisted exam generation from prompts or text-based files, supporting efficient and adaptable test construction.
For the trial sessions, the exam content consisted of introductory questions in Social Studies, English, and Science, derived directly from the locale’s syllabus. These questions were intentionally selected to reflect familiar subject matter for participants, ensuring that the focus of the evaluation remained on the detection system’s performance rather than on the difficulty of the test items. By integrating syllabus based content into the trial web app, the study maintained contextual relevance to the institution while generating a dataset that future researchers can build upon.













Figure 8. Sample Questions
  


Figure 9. Cheating Setup
 
The cheating setup consists of a printed compiled copy of all questions from every subject examination, which is used as one of the the primary external reference materials during the trials. The test takers were informed to only asnwer up to two questions using their general knowledge, and use external resources such as the paper cheatsheet, the Copilot tab, and additional browser tabs while answering the rest of the exam. This arrangement was designed to simulate realistic cheating behavior under controlled conditions. The printed cheat sheet was allowed to be moved freely within the testing environment, which created a natural and flexible setup that reflected authentic test taking scenarios. This approach ensured that the observed behaviors were representative of genuine cheating tendencies, supporting the study’s goal of analyzing detection accuracy in realistic contexts.
## Software Testing Techniques
To ensure the reliability, accuracy, and overall performance of both the web based exam delivery platform and the Suspicious Exam Behaviour Detection System, the study incorporates a structured multi level software testing approach. This testing process aligns with the KANBAN methodology by allowing iterative refinement based on continuous feedback and observed system behavior.
## Unit Testing
Unit Testing was conducted to validate the correctness of individual components before integration into the full system.
This includes:
- Face Landmarkers Detection System
- Iris Position Estimation System
- Face Position Estimation System
- Behavioural Scoring System
- File Creation System (Video Replay and Session Logs File)
- Django Fullstack Web Application
Each unit test verified that isolated modules performed as expected under normal and edge case conditions. This ensured that foundational operations, such as facial landmark extraction and gaze coordinate calculations, were accurate before combining them into larger workflows. Early identification of bugs significantly reduced debugging complexity during later stages.
## Integration Testing
Once individual modules were validated, Integration Testing examined how these modules interact when combined into logical subsystems. Integration testing is primarily about how the detection system will be integrated into the web application prototype. The integration testings outside the scope of web application integration are about the gaze tracking system interacting with the SEBDS. 
This phase focused on:
- Integration of the gaze tracking module with the Django backend, ensuring that calculated gaze coordinates are correctly transmitted, logged, and interpreted in real time.
- Synchronization between the exam interface and behaviour scoring system, validating that keypress logs, gaze data, and exam timers align without delays.
- Database integration, ensuring exam responses, session events, and analytics are stored correctly.
- Communication between frontend and backend, especially during high frequency events such as rapid gaze updates or continuous keypress detection.
Integration Testing ensured that module interactions did not generate inconsistencies; unit module compatibility issues do not arise during runtime and runtime processes which require the system to interact with each individual unit modules.
## System Testing
System Testing assessed the entire service as a cohesive system to evaluate its readiness for real world exam environments. 
This evaluation included:
- End to end exam simulations, where students completed full assessments while the detection system monitored behavior.
- Functional accuracy evaluation, verifying that suspicious behaviour scores, keypress logs, and gaze tracking outputs were integrated and displayed correctly in the proctor interface.
## Compatibility Testing
Compatibility Testing was conducted on the documented configurations. The completed compatibility test confirmed operation on Windows 11; broader cross-platform, cross-browser, hardware, third-party, and network validation remains outside the present evaluation.
This evaluation includes:
1.	Operating system checks, with the documented result limited to Windows 11.
2.	Browser compatibility testing, identified as a future extension across Chrome, Firefox, Edge, and Safari.
3.	Hardware variation assessments, confirming reliability on devices with differing CPU, GPU, RAM, and camera specifications.
4.	Third party integration validation, ensuring smooth interaction with supporting applications and frameworks.
5.	Network condition testing, assessing stability under varying bandwidths, latencies, and connection types.
## User Acceptance Testing
This User Acceptance Testing (UAT) survey aims to evaluate the usability, reliability, and ethical compliance of the MAKITEST: Suspicious Exam Behavior Detection System. The questions are designed according to ISO 9241 (Ergonomics of Human-System Interaction) and ISO/IEC 25010 (Software Product Quality Model) standards to assess the system’s effectiveness, efficiency, satisfaction, and data protection.
Respondents are asked to rate each statement based on their experience using the system. Please indicate your level of agreement using the scale below:
Detection Accuracy and Reliability
- The system accurately detects gaze direction, head pose, and keypress patterns during examinations.
- The detection of suspicious behaviors remains consistent across different test sessions.
- The system minimizes false positives when identifying irregular movements or actions.
- The detection modules (gaze, head pose, keypress tracking) perform reliably under varying lighting and camera conditions.
- The system maintains stable performance even when multiple detection features operate simultaneously.
Behavioral Data Output and Interpretation
- The behavioral data outputs (e.g., gaze heatmaps, event logs, and violation counts) clearly differentiate between cheating and non cheating trials.
- The data visualization effectively highlights patterns of off screen focus and irregular gaze behavior.
- The frequency and distribution of detected events provide structured indicators of behavioral irregularities for human interpretation.
- The system’s recorded metrics (e.g., gaze duration, off screen frequency, head pose deviation) are interpretable and support meaningful analysis.
- The overlap between normal and suspicious behaviors is observable and helps validate the need for human interpretation.
- The behavioral indicators correlate well with observed cheating tendencies in controlled trials.
- The data outputs assist proctors in making informed judgments rather than relying solely on automated classification.
System Responsiveness and Efficiency
- The detection system responds quickly to behavioral changes during exams.
- The latency between detection and alert generation is minimal.
- The system operates smoothly without causing noticeable lag or interruptions.
- The detection modules run efficiently on standard hardware configurations.
- The system maintains consistent performance throughout the duration of an exam.
Ethical and Privacy Considerations
- I was clearly informed about what behavioral data the detection system collects.
- The monitoring process felt transparent and respectful of user privacy.
- The system does not store or share personal data beyond what is necessary for detection.
- The detection system’s design promotes fairness and accountability.
- I trust that the system complies with institutional data protection standards.
Usability and Integration
- The detection system integrates seamlessly with the exam environment.
- The monitoring features do not interfere with normal test taking behavior.
- The calibration process for gaze and head pose detection is straightforward.
- The overall experience using the detection system was intuitive and non intrusive.

Documentation and Future Development
- The system’s documentation clearly explains how detection and data interpretation work.
- The calibration and setup instructions are easy to follow.
- The documentation provides sufficient information for troubleshooting.
- I believe the detection system can be improved through expanded datasets and model refinement.
- I would recommend further development and institutional adoption of this detection system.

Table 3. Likert Scale Reference
Scale	Description
1	Strongly Disagree
2	Disagree
3	Neutral
4	Agree
5	Strongly Agree

These responses will help the researchers identify areas for improvement and ensure that the system meets academic and ethical standards for online examination monitoring. All feedback will be treated confidentially and used solely for research and system enhancement purposes.
## Initial Suspicious Exam Behaviour Thresholds
To identify the initial thresholds of suspicious exam behaviour, the research will define suspicious exam behaviour as an action done by a user while taking the exam that can state that the user is using external resources to answer the exam. With this definition, the research concluded two starting controlled experiments to create a hypothesis on how to calculate the thresholds. These experiments are only initial experiments; more experiments will be conducted to further justify and re-calculate different thresholds and observed data for detection model development.
As the research take this approach, this method of testing can vary to the limitations given on this approach specifically the difference in behaviour and psychological aspects of test takers. The approach taken in these two experiments is the following: taking a Japanese Language Proficiency Test (JLPT) exam with a time limit, camera feed, and a keyboard and mouse tracker. This is to observe the keypress, gaze and face events. 

	The first experiment was a controlled JLPT N5 Level test which the tester is not allowed to use other resources to help with taking the exam. This is to observe the behaviour of a normal exam-taking behaviour.

	The second experiment was a controlled JLPT N5 Level test which the tester is allowed to use other resources to help with taking the exam. The resource used in this experiment is a second screen positioned on the top right of the user’s main monitor. The user has a Japanese Kanji Dictionary site in addition to the in-browser Copilot AI sidebar chat of the Microsoft Edge web browser.
The reason of it being a JLPT exam is that this helps in observing all the actions that the research is creating a basis on, which is suspicious exam behaviour. Using a JLPT exam makes use of a kanji dictionary, grammar books, translators, and the online software equivalents of all the above.
Table 4. Recorded Observations
	Recorded Data	Non-cheating Interpretation	Cheating Interpretation
Repeated gaze position in the same spot	-	Direction of the gaze
-	Time intervals
-	Keypresses	Habitual eye movement, checking time, time off screen 	Glancing at notes or another device/screen
Long fixation away from the screen	-	Duration of the gaze
-	Position of gaze
-	Keypresses
	Recalling memory, thinking deeply, or staring blankly	Searching for answers online or on other resources.  
Rapid gaze scanning	-	Number of directions
-	Speed of gaze changes	Environmental noise/distraction or stress	Searching for external resources for answers.
## Observation
In the research’s observation, there are key differences with taking the exam without external resources and taking the with external resources. The biggest differences are the duration length of gaze to a certain direction and keypresses. With the first experiment, the research has found there are only three notable lengths of gaze positions: “Up Center”, “Down Center” and “Up Left.” The primary reason for gaze changes is looking at questions, choices, and moving to the next question. Other lengthy duration of gaze changes is averting gaze from the screen or thinking deeply/recalling memory. The research has also shown that the user looks at the same position of the screen for most of the test duration.
Figure 10.1 Test 1 Recording
 

Figure 10.2. Test 1 Gaze Durations
 
In the second experiment, the user spends less time looking at the exam browser than the first experiment. The tester spends more time looking at the direction of the location of the exam resources the tester uses to answer the exam. It is also observed that there are rapid changes in gaze shifts with the primary reason of reading the exam questions while checking that it is the same on the exam resources the tester is using. 
One of the observed differences between the two test experiments as well are the keypresses and browser navigation. The tester tends to use shortcuts and tabs in and out of the exam browser to use and view the resources the tester has on hand. During this recording, the tester inputted a total of 187 keypresses during the exam. In addition to this, since it is possible to navigate the PC without using keypresses, the experiment recorded 28 paired tab-in and tab-outs either by keyboard shortcut or through mouse navigation.

Figure 10.3. Test 2 Recording
 





Figure 10.4. Test 2 Alt+Tab Capture
 





Figure 10.5. Test 2 Gaze Durations
## Initial Hypothesis
To create and conclude the related literature review, the study creates a hypothesis on how to create metrics to effectively detect suspicious exam behaviour and create a decision tree to calculate a quantifiable value to score suspicious exam behaviour.
Using the observed experiment data above, the key factor of detecting suspicious behaviour is the combination of the following: keypresses, gaze direction, gaze position, frequency of actions, intervals of actions, and duration of actions.
Figure 11.1 Camera Perspective-Based ANN Diagram
 
Using the artificial neural network (ANN) diagram done by Hu et al. (2024), the study adopts a similar neural network to justify the possible interpretations and factors that is observed and given varying weights and scoring values based on the research’s findings. In this neural network, the factors are based on any camera perspective data and inputs taken by the system. It involves gaze duration, gaze position, gaze direction, and cheating tools.


Figure 11.2 Browser-Based ANN Diagram
 
Similarly, this ANN follows the similar format. This ANN focuses on the browser-based events and keylogging that the system will track and add varying weights and scoring values based on the testing and unit testing done by this study.

To define initial thresholds from hypothesis of the two testing experiments, we shall define the following thresholds:



Table 5. Definition of Gaze Duration Terms
	Threshold
Short Duration	<19 seconds
Long Duration	>19 seconds
309seconds + 501seconds / (21 questions + 21 questions) = 19.2857 seconds per question

Table 6. Definition of Gaze Position Terms
	Threshold
Within Screen	Total Area < 25%
Outside Screen	Total Area > 25%



Figure 12. Screen Visualization
 
For the calculation of the short and long duration gaze duration, the study conducted a empirical approach. To define both terms, the study divided the length of the Up Center gaze time length to the total amount of questions in the online test. For the within and outside screen gaze position, the study applied a point to the left, right, upper and lower-most points of the estimated gaze circle of the gaze tracking system. If 25% or over of the total area of the four points is outside of the screen resolution, then it is defined as outside screen, otherwise, it is within screen.
## Suspicious Exam Behaviour Detection System
The Suspicious Exam Behavior Detection System is developed to uphold academic integrity in online examinations by identifying potential misconduct through continuous monitoring of students’ webcam feeds and keyboard inputs. The system employs a lightweight hybrid computer vision architecture combining face landmark tracking (using the Google MediaPipe Face Mesh model via the face_landmarker.task file) and a custom geometric scoring engine to detect anomalies in real time. Its purpose is not to replace human oversight but to provide structured evidence that assists proctors in making informed decisions.
To identify the most effective detection strategy, the study focused on minimizing computational overhead and device permissions to support standard browser environments. Rather than employing heavy deep-learning video segment classifiers like 3D Convolutional Neural Networks (3D-CNNs) or frame-based object detection models (such as YOLO or R-CNN), which require significant GPU resources and high-permission local installations, the proposed system utilizes a highly optimized coordinate-based tracking framework. It extracts 478 3D facial landmarks from a single camera feed in real time and translates them into spatial coordinates. The system then monitors:
1. Head Pose Estimation (Face Axis Processing): Evaluates head yaw and pitch angles to map coarse screen boundaries. Additionally, the system has an on-calibration-startup face normalization algorithm to compensate for tester quality differences such as height, leaning tendencies, and uncentered position within the camera frame.
2. Iris Position Detection: Tracks pupil offsets and eyelid height relative to calibrated thresholds to determine vertical and horizontal gaze.
3. Keyboard and browser event tracking: The standalone Windows prototype can use a non-blocking OS-level keyboard hook for selected forbidden shortcuts. The Django/browser path instead receives browser-reported key combinations, focus loss, and hidden-tab events through the WebSocket; it does not install a global keyboard hook on the server.
These spatial and event features are fed into a state-machine-driven scoring engine (SuspicionScoringProcessor) that evaluates behaviors against specific temporal and frequency thresholds, including a 1.5-second off-screen threshold, a 3-second side-look threshold, a 5-second down-look threshold, and more than six center-to-off-center shifts within a rolling 60-second window. If a threshold is crossed, a violation is logged to a session CSV file and frame-based video evidence is assembled asynchronously. The browser implementation is a prototype and does not by itself resolve all security, privacy, or deployment constraints of online proctoring.
The evaluation of candidate methods is conducted using established performance metrics. Accuracy is measured as the proportion of correctly identified behaviors relative to the total number of test cases, computed as:
 
Where TP denotes true positives, TN true negatives, FP false positives, and FN false negatives. Accuracy is chosen because it provides a general measure of overall correctness, which is essential in determining whether the system can reliably distinguish between suspicious and non suspicious behaviors.
To provide a more detailed assessment, Precision and Recall are also calculated. Precision reflects the proportion of correct positive detections among all positive detections, expressed as:
 
Recall measures the proportion of actual positive cases correctly identified, defined as: 
 
Precision is included because it evaluates the system’s ability to minimize false alarms, which is critical in avoiding unnecessary proctor interventions. Recall, on the other hand, ensures that the system does not overlook genuine cases of misconduct, thereby maintaining the integrity of the examination process.
The system aggregates all mapped gaze coordinates collected throughout the examination session to generate a post-exam gaze concentration heatmap. Utilizing the coordinates processed by the weighted fusion of head pose and iris landmarks, a density-based visualization (using a 2D Gaussian distribution) is plotted onto the screen coordinates.
In addition to detection accuracy, computational efficiency is assessed in terms of average processing time per frame, while resource utilization is measured through memory and CPU/GPU requirements. These criteria are included because the system must operate in real time under practical hardware constraints. A method that achieves high accuracy but requires excessive computational resources would not be feasible for deployment in typical online examination environments.
Figure 13. Visualized Eye-Gaze Concentration Heatmap
  
As shown in Figure 9, the resulting heatmap displays a high-intensity red focal point concentrated near the center of the screen, which represents normal, sustained visual attention on the active test interface. Transient glances or persistent focus shifts away from the questions are rendered as lower-density signatures (green and blue hues) in the outer zones. This visualization provides proctors with a clean, aggregate visual summary of the examinee's visual focus distribution over the course of the assessment, making it easier to identify anomalous, off-screen reading patterns during post-exam audits.
Figure 14. Suspicious Exam Detection Behaviour Showcase
## CV Model Framework Evaluation
The implemented system uses a MediaPipe facial-landmark model with iris refinement, followed by geometric gaze estimation and rule-based scoring. The selected implementation does not include facial recognition or object detection. Comparisons with other CV models are addressed through related literature and proposed as future work.
## Evaluation Criteria
To evaluate the different models, we used a set of tasks that we have determined to encompass each of the different aspects of what the system is observing and detecting.
- Face Movement Tracking - Assesses the accuracy of monitoring head orientation and facial movements to detect deviations from expected screen focus.
- Iris Tracking - Tests the precision of gaze analysis to determine whether the examinee’s eyes remain directed toward the exam interface or shift toward external materials.
Where a documented classification experiment is available, precision, recall, F1 score, and confusion matrices can be used to evaluate the resulting labels. These metrics should not be described as a comparison of multiple computer-vision models unless the corresponding model runs and results are provided.
## Computer Vision Algorithms
A central design decision in this research is to analyze temporal behavior patterns using a hybrid coordinate-and-state-machine approach rather than processing raw video clips through 3D Convolutional Neural Networks (3D-CNNs) or similar video classifiers (e.g., C3D, I3D). Heavy spatio-temporal video segment classifiers are computationally intensive, demanding high GPU memory and causing latency issues that render them unfeasible for real-time operation on standard student hardware.
Instead, our system utilizes a dual-component tracking framework. The face landmark extraction model (MediaPipe Face Mesh) outputs coordinates in milliseconds, which are then evaluated by a deterministic scoring processor. This design separates landmark detection (which uses a lightweight pre-trained model) from the behavioral classification (which runs on a rule-based state machine). This separation ensures that the system is computationally efficient, operates in near real time on standard setups (e.g., integrated graphics like Intel UHD 620), and provides full transparency and explainability in its scoring outcomes.
## Keypress Tracking Strategy
In parallel to the CV models framework evaluations, the proponents have also performed an analysis on the different strategies of Keypress tracking. As there are different ways to track and observe keypresses of a student during an online assessment, it is important to assess which strategies are most effective in online assessments.
These are the different keypress strategies that were chosen to be used for the evaluation process:
- Continuous Tracking – simple recording of the student's keypresses during the entire assessment session.
- Event-based Tracking – Focusing on shortcut usage detection or high APM (Actions Per Minute) 
In this strategy evaluation, the proponents have employed a different approach. Since continuous tracking have encompassed more data than event-based tracking, we will be tracking the following criteria:
Table 7. Keypress Strategies
	Continuous Tracking	Event-Based Tracking
Accuracy	Total keypress detection rate	Detection during and/or after defined shortcut events
Contextual Relevance	Identify noise from irrelevant keypresses	Completeness of data during key events
System Overhead	Monitor resource usage during full session	Monitor resource usage during triggered events
With how browser applications work, web browsers are designed to strictly follow the rules of tab focusing, which is a state of a web browser’s tab when directly interacting with the webpage. Since the locale testing used a computer installed version of the SEBDS, the test trials conducted in this study instead simulated the common shortcuts and interactions typically used and tracked in a focused browser tab during online examinations.
Any actions that interact outside of the webpage will update the state of the tab to be “blur”, which is the term used for the state in which the webpage is not the last interacted object in the user’s system. Actions that the proponents have found to cause a webpage to be in a blurred state are:
- Clicking out of the web browser app
- Using the shortcut Alt+Tab
- Clicking the search bar of the web browser app
- Clicking bookmarks, extensions and any interactable objects which is not in the HTML of the webpage.
## Gaze Tracking Algorithm
The proponents have created an algorithmic and geometric approach to tracking where the user is looking at the screen. Like the website, the gaze tracking system is built to integrate with the Django backend.
## Software Approach and Algorithms
- Face Tracking - Continuously monitors the position and movement of a student’s face during the exam to ensure attention remains directed toward the screen.
- Face Detection - Identifies the presence of a face within the camera frame, serving as the foundation for landmark tracking and gaze processing. This is not facial identity recognition.
- Image Generation - Produces synthetic or processed images (e.g., flagged frames or visual alerts) to assist proctors in reviewing suspicious behaviours.
- Image Enhancement - Improves the clarity and quality of captured images or video frames, ensuring accurate detection and reducing false positives.
## Camera Initialization and Configuration
In standalone mode, OpenCV’s cv2.VideoCapture() establishes a connection to a selected camera device. In browser mode, the camera is acquired through the browser MediaDevices API, converted to JPEG frames, and sent to the Django Channels consumer. The browser calibration page captures 640x480 frames at a target of 10 FPS, while the exam page captures 320x240 frames at a target of 5 FPS. These browser settings define the web prototype’s operating conditions.
After it has been established that the camera is outputting data, it will be using the MediaPipe Face Mesh solution, a machine learning-based facial landmark detection framework. The Face Mesh model is instantiated with specific parameters: static_image_mode=False for video stream processing, max_num_faces=1 to track a single user, refine_landmarks=True to enable high-precision iris landmark detection (providing 10 additional landmarks beyond the standard 468), and confidence thresholds of 0.5 for both detection and tracking to balance accuracy with processing speed. This configuration enables the extraction of 478 three-dimensional facial landmarks per frame, normalized to coordinate between 0 and 1 relative to the input image dimensions.
## Dual-Component Gaze Estimation Architecture
The system implements a hybrid approach combining two complementary methodologies:
## Head Pose Estimation Module
This component utilizes five strategically selected facial landmarks stored in the KEY_FACE_LANDMARKS dictionary within GazeTrackerState:
- Landmark 234: Left facial boundary (temple region)
- Landmark 454: Right facial boundary (temple region)
- Landmark 10: Superior facial boundary (forehead midpoint)
- Landmark 152: Inferior facial boundary (chin point)
- Landmark 1: Anterior facial reference (nose bridge)

Figure 15. Face Landmark Points
 
These landmarks define a three-dimensional coordinate system representing the face's spatial orientation. The algorithm constructs vectors from the nose bridge (landmark 1) to the lateral landmarks (234 and 454) to compute the yaw angle (horizontal head rotation), and from the nose bridge to the vertical landmarks (10 and 152) to compute the pitch angle (vertical head tilt).
The mathematical formulation of the system involves several sequential processes. Vector Normalization is first applied, where each directional vector is normalized to unit length to isolate angular information. Following this, Dot Product Calculations are performed to compute the angle between the face forward vector and the reference forward direction. These values are then converted into angular measurements, expressed in degrees, using Inverse Trigonometric Functions, specifically arcsine and arctangent.
To address high frequency noise and sudden movements, Temporal Smoothing is implemented. In this process, ray origins and directions are stored in deques and averaged using exponential moving averages. The resulting head pose data provides a coarse grained estimate of gaze direction. This approach is particularly effective for detecting large screen position changes, although it remains limited in precision for fine grained tracking
## Camera-Frame Position Correction Module
This component corrects the head-pose-derived screen position estimate based on where the subject's face is physically located within the camera frame. It operates within FaceAxisProcessor and is driven by four input values:
- face_center_x — Horizontal pixel coordinate of the detected face centre within the camera frame
- face_center_y — Vertical pixel coordinate of the detected face centre within the camera frame
- frame_width — Total width of the camera frame in pixels
- frame_height — Total height of the camera frame in pixels
These inputs are consumed each frame by update_anchor_from_face_position(), which computes a pair of screen-space offset values (_anchor_offset_x, _anchor_offset_y) that are subsequently applied inside get_estimated_screen_position().
The mathematical formulation of the correction involves two sequential operations. Spatial Normalisation is first applied, mapping the face centre from absolute pixel coordinates into a normalised deviation relative to the frame centre:
 
This produces values in the range [−0.5, 0.5][−0.5, 0.5], where (0,0)(0,0) indicates a perfectly centred face and the extremes represent a face at the edge of the frame. Screen-Space Projection is then performed, scaling the normalised deviation linearly onto the target screen resolution (1920×1080):
 
These offsets are added to the angle-derived screen coordinates before the result is clamped to the screen bounds. A face centred in the frame produces a zero offset and leaves the head-pose estimate unchanged; a face displaced toward a frame edge shifts the estimated gaze position in the same direction by a proportional number of screen pixels.
This correction addresses a systematic bias inherent to head-pose-only gaze estimation: when a subject sits off-axis relative to the camera, their head-rotation angles alone underestimate or overestimate how far across the screen they are looking. By anchoring the estimate to the face's position within the frame, the module compensates for this parallax-like error without requiring additional sensor data. The approach is lightweight and runs per-frame with negligible computational cost, although its accuracy is bounded by the quality of the underlying face-centre detection and assumes a fixed camera-to-screen geometric relationship.
## Iris Position Detection Module
This module achieves higher precision by analyzing eye-specific anatomy. The implementation leverages two sets of landmarks:
- Left Eye Landmarks: A 17-point contour (indices 33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246, 130) delineating the left eye boundary, including eyelid margins and eye corners.
- Right Eye Landmarks: A symmetric 17-point contour (indices 263, 249, 390, 373, 374, 380, 381, 382, 362, 398, 384, 385, 386, 387, 388, 466, 359) for the right eye.
5.1.1.	Screen Gaze Processing Pipeline:
5.1.1.1.	Bounding Box Construction:
The get_eye_bbox() function computes axis-aligned minimum bounding rectangles around each eye by identifying the minimum and maximum x and y coordinates from all eye landmark points, with an additional 5-pixel padding (self.padding = 5) expanded asymmetrically (+20 pixels horizontally, +10 pixels vertically) to ensure complete eye region capture while accommodating eye movement.

5.1.1.2.	Iris Center Calculation:
The get_iris_center() function processes MediaPipe's refined iris landmarks (the additional 10 landmarks enabled by refine_landmarks=True). For each eye, five iris boundary points are extracted, and their centroid is computed through arithmetic mean operations on both x and y coordinates. This centroid represents the iris center in absolute pixel coordinates within the camera frame.
Normalized Position Computation - The iris center coordinates are normalized relative to the eye bounding box dimensions. By computing the ratio of the iris center's offset from the left edge to the total box width (horizontal normalization) and from the top edge to the total box height (vertical normalization), the algorithm produces scale-invariant iris position values between 0 and 1, representing the iris position within the eye socket regardless of camera distance or face size.
Binocular Fusion - The normalized positions from both eyes are averaged to produce a single, robust iris position estimate. This binocular approach increases accuracy by canceling out asymmetric noise and compensating for individual eye variations.
## Distance Estimation Subsystem
The standalone tracking path includes a polynomial distance-estimation component for experimental parallax compensation. This component is separate from the Django `GazeSession` pipeline, so distance calibration is not part of the web prototype’s active tracking stages. The model is defined by:
- Training Data: Five calibration points mapping facial width in pixels (y_dist = [240, 132, 350, 560, 200]) to known physical distances in centimeters (cm_dist = [25, 50, 15, 20, 30])
- Polynomial Coefficients: A second-degree polynomial (deg=2) is fitted using NumPy's polyfit() function, producing quadratic coefficients stored in dist_coff
- Real-time Estimation: During tracking, the algorithm measures the pixel distance between left and right facial landmarks (234 and 454), evaluates the polynomial using these coefficients, and outputs the estimated distance in centimeters
In the standalone experimental path, this distance estimate can be used to adjust gaze-mapping sensitivity. The Django web session uses the calibrated head-pose and eye-position stages without active distance-based correction.


Figure 16. Camera Distance Algorithm and Logic
## Calibration Protocol
The system implements a structured calibration sequence that establishes user-specific gaze mapping parameters. In the Django path, calibration begins with a head-pose baseline, followed by five eye-calibration stages: center, up, down, left, and right. Each eye stage collects 60 valid samples.

Table 8. Calibration Protocol Stages
Stage	Description
Stage -1 - Head-Pose Baseline	The user sits in a neutral position while the system records the current head-pose reference.
Stage 0 - Center Calibration	The user focuses on the screen center. The system records pupil and iris-box-height samples to establish the user’s neutral eye measurements.
Stage 1 - Upward Calibration	The user looks at the top of the screen. Samples are collected to establish the upward eye measurements.
Stage 2 - Downward Calibration	The user looks at the bottom of the screen. Samples are collected to establish the downward eye measurements.
Stage 3 - Left Calibration	The user looks at the left edge of the screen. Horizontal samples are collected to establish the leftward eye measurements.
Stage 4 - Right Calibration	The user looks at the right edge of the screen. Horizontal samples are collected to establish the rightward eye measurements.

Each calibration stage contributes to a completion state. The web implementation writes the resulting thresholds to `eye_calibration.json` and may also store them in the Django database for the student. Calibration data is therefore available for the session and authorized persistence workflow.

5.1.2.	Active Tracking Phase
Upon completion of calibration (calibration_stage = 5), the web session enters continuous tracking mode. The process_frame() method executes the following pipeline for each captured frame:
Landmark Detection: MediaPipe processes the frame and returns 478 facial landmarks with three-dimensional coordinates (x, y, z normalized values plus visibility scores).
Head Pose Computation: The five key facial landmarks are extracted, and vector operations compute current yaw and pitch angles, adjusted by calibration offsets.
Iris Position Extraction: Eye regions are isolated using bounding boxes, iris centers are calculated, and normalized positions are computed relative to eye boundaries.
5.1.3.	Gaze Coordinate Mapping:
Horizontal Mapping - The normalized iris horizontal position is mapped through piecewise linear interpolation between calibration thresholds to produce an x-coordinate between 0 and 1
Vertical Mapping - The normalized iris vertical position undergoes similar interpolation using vertical thresholds to produce a y-coordinate between 0 and 1
Weighted Fusion - When both estimates are available, the gaze-fusion module assigns 40% weight to the head-based position and 60% weight to the eye-based position: combined_gaze = 0.4 * head_gaze + 0.6 * iris_gaze. If one estimate is unavailable, the available estimate is used.
Temporal Filtering - The combined gaze coordinates are appended to history deques. A moving average filter is applied to these histories, producing the final smoothed gaze position stored in the weighted screen position variable.
Screen Coordinate Conversion - The normalized coordinates (0-1 range) are multiplied by screen dimensions to produce absolute pixel coordinates representing the estimated point of regard on the examination interface.
5.1.4.	Output and Integration
The get_screen_position() method returns the final normalized gaze coordinates as a tuple (x, y) where both values range from 0.0 to 1.0. This standardized output format enables seamless integration with the Django backend, where gaze data can be logged to the database via the models defined in models.py, transmitted to the frontend for real-time visualization, or analyzed for examination integrity assessment (detecting prolonged off-screen gaze, unusual gaze patterns, or absence of face detection indicating the examinee has left their station).

## Machine Learning Approach
Random Forest Classifier is used as an exploratory session-level prediction model. It consumes the stored heatmap and event-log features and returns a predicted class through the model’s `predict()` method. The confidence level is the probability assigned by `predict_proba()` to that predicted class. This confidence is distinct from the rule-based 0-or-100 event score, and the available results should not be treated as independent deployment validation.

## Web Application Framework and Architecture
To create our Exam Delivery Application which will implement and integrate our suspicious behaviour detection system, we are using the Python Django framework. 
Python Django is a high-level web framework which is known for its scalability, security and convenient maintenance. The framework uses the MVT Architecture which means Model, View and Template.
Model is involved in handling how data is defined and stored; Views are the ones that handle requests and decisions of what data to output; Templates are responsible for what the end users are going to be interacting and experiencing in the browser.
To start, the homepage content is where the users can login and register before they are able to access the content of the website. Once the user logs in, they will be able to see the contents of the website depending on their roles 


Table 9. System Roles and Access
Role	Content
Student	
The system allows each examinee to maintain a User Profile, which serves as the foundation for personalized access. Through this profile, students can View their own assessment scores to monitor performance and progress. They are also able to View their own assessment session analytics, providing insights into their test taking behavior and outcomes. Finally, the platform enables them to Access and take their own assessments, ensuring a streamlined and secure examination process.
Proctors	
The system provides proctors with a User Profile that serves as the basis for managing their classes and assessments. Through this profile, they can View the class roster, allowing them to monitor enrolled students. Proctors are also able to View their own class assessment scores, ensuring transparency in performance tracking. To maintain accuracy, the platform includes Assessment Score Correction Tools, which allow adjustments when necessary. In addition, instructors can View their own class assessment session analytics, offering insights into student behavior and outcomes during examinations. Finally, the system equips proctors with Assessment Creation and Publishing Tools, enabling them to design, administer, and release assessments directly through the platform.

Admin	
The system provides administrators with CRUD access to the user database, allowing them to create, read, update, and delete user records as needed. In addition, administrators are granted CRUD access to the exam database, enabling them to manage examination data through the same set of operations. These functions ensure that administrators can maintain both user information and exam records efficiently and securely.
Students will be able to go through the web app to view their respective profile account, assessments grades, assessments session analytics and assessments they need to take; Proctors will be able to see their class rosters, exam scores, exam session analytics, and assessment creation, publishing and modification tools; Administrators will have access to user databases and exam databases, which they have Create-Read-Update-Delete (CRUD) access to.
## Exam Delivery Module
This module will allow the proctors to create assessments, customize exam access, import question banks and designate to the students/class.
Table 10. System Features
Feature	Description
Import Question Banks	
Accept formatted Excel sheets that consists of a question and an answer by batch / individually
Assessment Creation and Modification Tools	
The system enables instructors to Generate an exam using a selected question bank, ensuring that assessments are drawn from predefined and relevant materials. In addition, instructors can Modify the type of each question individually, allowing flexibility in tailoring the format of the assessment. They are also able to Modify the score weight of each question, providing control over how each item contributes to the overall evaluation.


Password-Locked Assessments	
Generate a computer-generated key to proctors for better security of assessment
Assessment Customization Tools	
The system allows instructors to Set due dates, start times, and end times for assessments. They can also Set an exam timer to regulate duration and Assign class designations to ensure proper distribution of exams.
## Proctor-Side Interface
## Authentication Process
The system is designed to use role-based access control for a secure and personalized user experience. The application provides homepage authentication and role-specific dashboards, while the current camera WebSocket permits anonymous connections unless the `GAZE_REQUIRE_AUTH` setting is enabled. When authentication is enforced, user credentials are validated and permissions are assigned based on predefined roles. This approach streamlines navigation by directing authorized users to dashboards tailored to their responsibilities.
## Dashboard Overview
Upon successful login, users are redirected to their respective dashboards, which function as the primary interface for system interaction. The dashboard is designed to provide a view for ongoing and completed examinations, leveraging dynamic content rendering for efficiency. Each exam entry includes a redirect button to the exam submission list of the selected exam, enabling proctors to review student performance comprehensively. Features include:
Exam Summary Cards: Display exam status (active, completed), schedule, and quick-access buttons.
Submission Management: Allows proctors to view student names, scores, and detailed answer sheets. A return navigation button ensures seamless movement between submission views and the main dashboard.
Navigation Tabs: 
Dashboard - Default landing page post-login.
Exams - Central hub for exam lifecycle management.
Help - Provides FAQs and integrated support channels for technical assistance.
The dashboard architecture prioritizes usability and responsiveness, ensuring minimal latency during data retrieval and interaction.
## Exam Management Module
The Exams tab encapsulates the core functionalities for assessment administration, structured around CRUD (Create, Read, Update, Delete) operations. Key features include:
Exam Creation: Redirects to a dedicated form requiring essential metadata such as:
- Exam title and instructions for clarity.
- Scheduled date and time parameters for controlled access.
- Access code for secure entry.
- Attempt limits and duration settings to enforce fairness.

Upon submission, the system validates input data and returns a success or error message. Successful creation triggers the update of the exam list within the Exams tab.
Exam Modification: Facilitates dynamic question management, including addition, deletion, and editing of items. This feature supports multiple question formats and integrates validation checks to maintain structural integrity.
Exam Deletion: Implements confirmation protocols to prevent accidental data loss, ensuring compliance with data governance standards.
Submission Review: Provides granular insights into student responses, enabling proctors to audit performance and detect anomalies indicative of academic dishonesty.
The module is engineered for scalability, allowing concurrent operations without compromising system performance. Its design aligns with principles of modularity and maintainability, ensuring adaptability for the future.

1.	Unified UML Class Diagram (Eye Tracking with Integrated Behaviour Detection System)
Figure 17. Class Diagram
 
The Unified UML Class Diagram represents a highly modular, multi-threaded object-oriented architecture designed for real-time computer vision processing, sensor fusion, and behavioral anomaly detection. The system's execution lifecycle is driven by the central orchestration process, main_trackerprocess.py, which instantiates the component processors and coordinates data passing within a high-frequency main processing loop.
The architecture is divided into four main operational layers:
Concurrency and Input Ingestion: The FrameBufferProcessor leverages a dedicated background capture thread to continually update a thread-locked video buffer from the physical camera device, eliminating primary thread blocking. Concurrently, the KeypressTrackProcessor registers low-level OS hotkey hooks via the keyboard library, storing unauthorized combinations (e.g., app-switching shortcuts) in a synchronized buffer to log cheating vectors.
Feature Extraction and Geometry: The FaceLandmarkerProcessor and EyeLandmarkerProcessor utilize MediaPipe FaceMesh to extract 3D coordinates. The standalone tracking path includes the FaceDistanceProcessor, which applies a quadratic fit to inter-pupillary distance for experimental camera-distance estimation. The web path uses the FaceAxisProcessor to derive head yaw and pitch, while eye landmarks are mapped by the EyeGazeProcessor to calculate iris and eyelid-opening features used during the 60-sample calibration stages.
Sensor Fusion and Coordinate Mapping: The EyeScreenPosProcessor converts raw pupil offsets into smoothed, jitter-free monitor coordinate points. The GazeDirectionProcessor performs sensor fusion, applying a weighted average (40% head-pose yaw/pitch, 60% eye coordinate position) to establish a unified screen coordinate representing the examinee's point of regard. Throughout the exam session, the HeatmapProcessor plots these coordinates, applying a large Gaussian blur kernel at session close to compile a JET thermal attention map (session_heatmap_png).
Behavior Scoring and Proctoring: The SuspicionScoringProcessor applies rule-based thresholds to fused gaze coordinates and reported keyboard or browser events. On violation triggers, it writes event details to the session CSV and initiates frame-based video capture. A background daemon thread encodes the pre-trigger and post-trigger frames into an MP4 violation clip without blocking the main tracking thread; the exact temporal duration depends on the incoming frame rate.


2. UML Subsystem Diagrams
Figure 18. Core Orchestration and Input Subsystem

 
The Core Orchestration and Input Subsystem is responsible for camera initialization, non-blocking frame buffer ingestion, and system-level hotkey hook monitoring. By utilizing multi-threading, the `FrameBufferProcessor` executes an asynchronous capture loop to continuously update a thread-locked frame buffer, eliminating main-loop latency associated with raw webcam input reads. Simultaneously, the `KeypressTrackProcessor` registers low-level operating system hooks via the `keyboard` library, intercepting unauthorized shortcuts (e.g., `alt+tab` or `print screen`) in a thread-safe list to identify system evasion. The central `main_trackerprocess` acts as the orchestrator, coordinating the lifecycle of these input streams and driving the downstream gaze-estimation and proctoring algorithms.
Figure 19. Face Tracking and Head Pose Subsystem
 
The Face Tracking and Head Pose Subsystem handles the spatial geometry of the user’s face to estimate head orientation angles. The `FaceLandmarkerProcessor` passes captured frame arrays to MediaPipe’s FaceMesh model, utilizing temple, chin, and forehead landmarks to compute a smoothed face-forward direction vector. The standalone tracking path also contains a `FaceDistanceProcessor` for polynomial distance estimation. The `FaceAxisProcessor` computes horizontal yaw and vertical pitch angles from the head direction vector, applying user calibration offsets to project a head-pose-based gaze point onto the monitor coordinates.


Figure 20. Eye Tracking and Calibration Subsystem

 
The Eye Tracking and Calibration Subsystem is responsible for high-precision pupil/iris contour tracking, multi-stage user threshold calibration, and mapping pupil offsets to screen coordinate positions. The `EyeLandmarkerProcessor` isolates eyelid margins and irises, delegating geometry tasks to the `EyeGazeProcessor` which computes scale-invariant pupil offsets and vertical eyelid opening heights. During calibration, the `EyeCalibrationProcessor` records 60 coordinate samples across five target quadrants to generate user-specific threshold maps in a session configuration dictionary. Finally, the `EyeScreenPosProcessor` interpolates these thresholds using an Exponential Moving Average (EMA) filter to convert raw iris coordinates into smoothed, jitter-free $(X,Y)$ pixel screen coordinates.
















Figure 21. Gaze Fusion and Heatmap Subsystem
 
The Gaze Fusion and Heatmap Subsystem combines independent directional coordinates to produce a single stabilized focus coordinate and records long-term visual attention charts. The `GazeDirectionProcessor` takes the raw coordinates from the head pose and eye-tracking modules, calculating a weighted average ($40\%$ head weight, $60\%$ eye weight) to output a fused focus coordinate. The `HeatmapProcessor` continuously appends these fused points to a coordinate list throughout the exam. Upon session completion, it applies a large Gaussian blur kernel to smooth the points and maps them to a JET thermal color spectrum (masking empty areas to pure black) to generate a visual attention heatmap file.
Figure 22. Sample Generated Gaze Attention Heatmap Output (session_heatmap_TIMESTAMP.png)
 





Figure 23. Behavior Scoring and Proctoring Engine Subsystem
 
The Behavior Scoring and Proctoring Engine Subsystem operates as the central decision-making unit, validating user actions against behavioral thresholds and recording visual evidence of violations. When the `update()` method evaluates a threshold transgression, such as a forbidden shortcut, an off-screen gaze duration limit, or frequent center-to-off-center transitions, it registers a violation, logs it to a session CSV file, and activates the video capture sequence. To capture context, a circular `frame_buffer` queue stores 30 frames before a trigger, and the scorer accumulates 30 post-trigger frames. A background daemon thread is then spawned to execute `_save_video_async()`, merging the frames into an MP4 video clip using the configured `avc1` codec. The CSV stores the event timestamp and video filename, while the temporal duration of the clip depends on the actual input frame rate.
Figure 24. Sample Generated Session Log Entry 
(session_log_TIMESTAMP.csv)
 



Figure 25. Sample Generated Violation Video Clip Frame (TIMESTAMP_violation_REASON.mp4)
 
3. Web Application System Architecture and Design
Figure 26. Web Application System UML Diagram
 
The web application architecture integrates several subsystems which are designed to work together within a modular Django framework. Each subsystem performs a distinct function such as data persistence, identity management, routing, business logic, and computer vision, so that the entire system operates securely and efficiently. This structure ensures scalability and maintainability, which is essential for managing examinations and proctoring activities. The UML diagram below presents how these subsystems interact, which is through coordinated data flow and role based operations that form a unified and intelligent exam management environment.
3.1 Persistence and Domain Modeling
The Persistence and Domain Modeling Subsystem establishes the data schema through Django’s ORM. `homepage.CustomUser` stores account roles and class designation; `StudentExamAttempt` stores exam attempts, grades, proctoring identifiers, violation counts, and prediction fields; `StudentTrackingThresholds` stores student calibration thresholds; and `ProctoringSessionFiles` registers calibration files, heatmaps, CSV logs, and violation videos. Exam and question entities are owned by the `teacherside` application. These models provide the persistence structure for exam delivery and proctoring artifacts.










Figure 27. Persistence and Domain Modeling UML Diagram
 

3.2 Identity, Authentication, and Access Control
The Identity and Access Control Subsystem governs secure registration and role based authorization. The SignUpForm extends Django’s UserCreationForm with application specific fields such as email, birthday, and LRN_number, enforcing role dependent validation rules during submission. Its atomic save() method guarantees synchronized creation of both the base User record and the corresponding role extension. Access control is further reinforced by the login_required_role decorator, which validates both authentication and administrator authorization before permitting entry into protected views. This dual factor gate ensures that newly registered accounts remain inactive until explicitly approved, thereby safeguarding sensitive exam delivery surfaces against unauthorized access.

Figure 28. Identity, Authentication, and Access Control
 
3.3 Request Routing and URL Dispatch
The Routing and Dispatch Subsystem partitions the application’s URL namespace to enforce role boundaries and prevent route collisions. The Django project delegates public authentication and landing pages to `homepage`, student operations to `studentside`, camera calibration and WebSocket handling to `camera`, and exam management to `teacherside`. The Django admin interface is mounted separately at `/admin/`. This structured delegation isolates functional domains while maintaining a coherent global routing strategy.

Figure 29. Request Routing and URL Dispatch
 
3.4 View Controllers and Business Logic
The View and Business Logic Subsystem orchestrates the request response cycle across role specific modules. Public pages such as home, about, and contact are served unconditionally, while registration is handled by site_signup, which validates and persists new accounts. Teacher facing controllers manage the full exam lifecycle, including authoring, modification, and deletion, with helper functions (update_exam_question_count, update_exam_scores, update_exam_details) maintaining consistency across derived fields and student submissions. Student facing controllers provide dashboards, exam taking interfaces, and results views, ensuring seamless interaction with assigned exams. Each controller is guarded by role specific decorators, reinforcing the principle of least privilege and aligning business logic with identity constraints.
Figure 30. View Controllers and Business Logic
 
3.5 Computer Vision and Camera Streaming
The Computer Vision and Streaming Subsystem delivers real-time gaze tracking and optional annotated frames to support behavioral analysis. In the browser implementation, JPEG frames are sent to a Django Channels WebSocket, where `GazeSession` processes face and eye landmarks and returns `frame_result` JSON messages. These messages can include gaze positions, gaze direction, head-pose values, suspicion state, and optional debug frames. This WebSocket design provides the data needed to correlate gaze estimates with session events.
Figure 31. Computer Vision and Camera Streaming
## Gaze Tracking Submodules Testing
Table 11. Gaze Tracking
No.	Test Case	Objective	Testing Procedure	Outcome	Comments
1	Camera Initialization	Ensures webcam is initialized and processed frames properly	Ran tracking system using default plug-and-play camera hardware and settings	Successful	Camera freezes during calibration protocol; however, it is only the frame processing and will continue properly streaming frames after each calibration stage is complete.
2	Landmarks Detection	Verify if system properly captures face landmarks	Ran landmark detection code snippet on camera-facing face with overhead lighting and monitor screen lighting only.	Successful	Landmark detection is consistent and accurate on both testing. A complete 90-degree angled face from the camera fails to get detected. The system now has fallback protocol for this instance and the system will continue running and waiting for a face to be detected.
3	Iris Direction Detection	Verify that iris tracking system outputs the correct direction based on calibration	Ran the gaze tracking system for 5 different users using the same face orientation testing procedure for Test Case 2.	Successful with comments 	Gaze tracking system with only iris tracking is sensitive
4	Face Axis/Direction Detection	Verify that face direction tracking is correctly 	Ran the gaze tracking system. Tested accuracy of estimated gaze position based on face axis	Successful with comments 	Gaze tracking system is significantly more stable and accurate when face axis and iris direction systems are cross validating outputs. A complete 90-degree angled face from the camera fails to get detected. The system now has a fallback protocol for this instance.
5	Calibration Protocol	Verify that calibration protocol on gaze tracking is saved properly and consistently captures correct directions	Ran the calibration protocol on camera-facing face of 5 different users and verified that gaze tracking systems is consistently tracking correct directions and positions	Successful with comments 	While still able to consistently track gaze direction, if a user utilizes the calibration data of a different session. Some edge cases of slightly different face axis position from the start of the tracking may output a direction close, but not exactly the right gaze direction. This can be minimized by using a calibration protocol for each testing.

Table 12. Keypress Track
No.	Test Case	Objective	Testing Procedure	Outcome	Comments
1	Capture Character Keypresses	Verify that system tracks the any character or symbol pressed on the keyboard	Done by accomplishing a mock test in the exam delivery app	Successful with comments	Only tracks when within the exam delivery app tab or when an extension or software that keeps a selected tab on “focus” while out of the tab.
2	Capture shortcuts	Verify that system tracks the shortcuts pressed on the keyboard	Done by accomplishing a mock test in the exam delivery app	Successful with comments	Only tracks when within the exam delivery app tab or when an extension or software that keeps a selected tab on “focus” while out of the tab.
3	Save session keypress logs	Verify that the system saves keypresses after runtime is terminated.	Done by using the computer software version of the Suspicious Exam Behaviour System	Successful with comments	As it is tested on the computer app version of the system, this system tracks all keypresses even outside the exam app, which is out of the scope and specifications of the web app prototype of the system.

Table 13. SEBD and Logging
No.	Test Case	Objective	Testing Procedure	Outcome	Comments
1	Directional Gaze Duration Triggers	Ensure that brief tracking dropouts (e.g., blinks, quick posture adjustments) do not trigger false alerts, while sustained absences do.	Cover the webcam or close eyes for a brief moment (< 1s), then block the webcam or close eyes for a sustained period (> 2s) and check for alerts.	Successful	
The implementation of a 1.5-second buffer successfully eliminated false positives from rapid eye blinks and natural head movement, only logging a violation when sustained off-screen behavior occurred.
2	Directional Gaze Duration Triggers	Verify that different look-away directions (Down vs. Up/Left/Right) trigger using their respective configured time thresholds.	Look down at the desk continuously for 6.0 seconds, then repeat looking sideways (e.g., Left) for 4.0 seconds.	Successful with comments	Validates that looking down uses a higher threshold (5.0s) to accommodate typing or looking at scratch paper, while side directions use a tighter threshold (3.0s). The logged violation names correctly map to <gaze_direction>_duration.
3	Frantic Eye Movement Frequency	Verify that rapid, repetitive shifts of gaze away from the screen are flagged.	Shift gaze from Center to off-screen zones and back 7 times within a 30-second window.	Successful	Successfully flags frantic scanning patterns using a rolling 60-second queue of transition timestamps. The queue is cleared immediately after a trigger to avoid duplicate alerts.
4	Asynchronous Video Clipping	Verify that frame-based video evidence is recorded and assembled when an event is flagged.	Trigger a behavioral violation (e.g., look sideways for 4 seconds) and check the output directory for the compiled video.	Successful with comments	The system stores 30 frames before the trigger and 30 frames after it, then saves them on an asynchronous daemon thread. The temporal duration represented by the clip depends on the incoming frame rate.
5	Session Log (CSV) Generation	Verify that the system generates a structured CSV session log tracking transitions, behaviors, scores, and video filenames.	Complete a proctored exam session with normal behavior and triggered violations, terminate runtime, and inspect session_log_<timestamp>.csv.	Successful	Generates a standardized row format mapping gaze directions to start/end timestamps, violation labels, rule-based event scores (100 for a triggered violation, 0 for a normal state), and the exact matching video evidence filename for review. A triggered violation is not equivalent to a confirmed cheating finding.

Table 14. Exam Delivery
No.	Test Case	Objective	Testing Procedure	Outcome	Comments
1	Integration Compatibility with SEBDS	Verify that the web-app structure will easily be able to incorporate changes to the SEBDS	In parallel with the Exam Delivery Web app development, a prototype SEBDS version was developed with web app integration in mind 	Successful with comments	The web app and the integration of the SEBDS system was successful. To note however, any changes to the SEBDS will still require knowledge of the web app structure to integrate the system properly.
2	Student-specific dashboards and tools	Verify that the “Student” accounts can access and manage the actions and data stated in the web app development documentation.	Ran a full test of usage of the actions, views, and access the role are documented to be able to do.	Successful with comments	As this is a proof of concept of a full web-based exam delivery app, recommendations will need to be recorded for future researchers.
3	Proctor/Teacher-specific dashboards and tools	Verify that the “Teacher” accounts can access and manage the actions and data stated in the web app development documentation. 	Ran a full test of usage of the actions, views, and access to the role are documented to be able to do.	Successful with comments	As this is proof of the concept of a full web-based exam delivery app, recommendations will need to be recorded for future researchers.
4	Role-Restricted Access to Role-Specific Webpages	Verify that users with “Student” and “Teacher” roles can only view their own respective 	Done by copying the URL address of respective opposite roles while logged in to accounts with opposite roles. Testing while not logged in was also checked in this test case.  	Successful	

Table 15. Integration Test
No.	Test Case	Objective	Testing Procedure	Outcome	Comments
1	SEBDS integration testing with Gaze Tracking System	Verify that the SEBDS accomplishes its processes correctly when direction data from Gaze Tracking System is given.  	Ran the full system, calibrated the gaze tracking system and looked in every direction for 5 seconds each.	Successful	
2	SEBDS integration testing with Keypress Tracking System	Verify that SEBDS accomplishes its processes correctly when keypress logging data from the Keypress Tracking System is given.	Ran the full system, calibrated the gaze tracking system and took a mock test while only using books, browser search, and browser AI chat sidebars.	Successful	
3	Exam Delivery App integrated with the SEBDS	Verify that the SEBDS can be initialized and used in a web app format	Used an earlier version of the SEBDS to be integrated with the Exam Delivery Web App Prototype developed,	Successful with comments	Since the SEBDS version used is an earlier rendition, there will be a need to update some aspects of the web app framework. This is accounted for by encapsulating each module and its processes in their separate code files compared to the all-in-one packaged version of the initial SEBDS versions.


Table 16. System Test
No.	Test Case	Objective	Testing Procedure	Outcome	Comments
1	Covering face/Loss of face detection during calibration	Checking what the system will do when calibration was interrupted by loss of face detection/deliberately covering face	Tester was instructed to cover face/turn face away from camera and other actions which led to loss of face detection	Unsuccessful	Crashes when face becomes undetected during calibration process
2	Covering face/Loss of face detection during test session	Checking what the system will do when session was interrupted by loss of face detection/deliberately covering face	Tester was instructed to cover face/turn face away from camera and other actions which led to loss of face detection	Successful with comments	System continues to run and stays at the last saved point of estimated screen position. Resumes when the face is detected again.
3	Calibration setup image background change	Check if difference in background of calibration setup image changes accuracy of system	Tester with problematic test sample was instructed to retake with a white background setup image versus a black background setup image	Successful	System accuracy has increased after change to white background
4	Wide eye peripheral tester	Check if system can estimate screen gaze position with outlier tester	Testers were found to have the ability to see the entire screen with minimal movement caught on camera feed. The tester was still instructed to partake in the system testing.	Unsuccessful with comments	The system was inaccurately tracking movements. Key factor is hardware limitations
5	Tester height	Check if there is significant bias towards tester of certain face position within camera frame 	Testers were made to sit the same chair distance from the testing desk	Successful with comments	System has a clear bias on testers whose face is located near the middle of the camera frame

Table 17. Compatibility Test
No.	Test Case	Objective	Testing Procedure	Outcome	Comments
1	Windows 11 Compatibility	To ensure that the system runs on Windows 11	Run the SEBDS and Web App prototype on a Windows 11 device.	Successful	
# Chapter 4: Results and Discussion
Fifteen participants completed the User Acceptance Testing (UAT) survey, which indicated high self-reported satisfaction across the listed categories. These responses describe participant perceptions of the prototype rather than independent measurements of detection accuracy or proof of minimal false positives. Under Detection Accuracy and Reliability, respondents evaluated their experience with gaze direction, head pose, and keypress outputs; the results are interpreted together with the system tests and implementation limitations.
For Behavioral Data Output and Interpretation, participants reported positive perceptions of the clarity of the generated data. The behavioral outputs, such as gaze heatmaps, event logs, and violation counts, were perceived as useful for comparing the reported experimental conditions. Respondents also recognized the overlap between normal and suspicious behaviors, which supports the system’s design as an aid to human interpretation rather than an autonomous judge.
In System Responsiveness and Efficiency, respondents gave high ratings for perceived responsiveness and stability. These survey responses describe user experience and should be distinguished from measured latency or resource-utilization benchmarks.
The Ethical and Privacy Considerations category received high agreement, indicating that respondents generally felt informed about data collection and perceived the monitoring process as respectful. These perceptions do not independently verify privacy compliance or institutional data-protection requirements.
Meanwhile, Usability and Integration responses were favorable regarding intuitiveness, intrusiveness, and calibration. These findings represent reported user perceptions of the prototype and should not be generalized beyond the tested participants and conditions.
Finally, in Documentation and Future Development, participants agreed that the system’s documentation was clear, comprehensive, and easy to follow. Most respondents strongly supported continued development and institutional adoption, emphasizing that expanded datasets and model refinement could further enhance performance.
Overall, the Likert scale results provide preliminary user-acceptance evidence for the prototype. They do not independently confirm technical reliability, ethical compliance, or the ability to distinguish cheating from non-cheating behavior.
Table 18. UAT Testing Results
Category	Description	Mean Score	Interpretation
Detection Accuracy and Reliability	Accuracy of gaze, head pose, and keypress detection; consistency across sessions	4.8	Strong agreement; highly reliable detection performance
Behavioral Data Output and Interpretation	Clarity and conclusiveness of behavioral data (heatmaps, logs, violation counts)	4.7	Strong agreement; data effectively differentiates cheating vs. non cheating
System Responsiveness and Efficiency	Speed, latency, and stability of detection modules during exams	4.6	High agreement; system operates smoothly with minimal lag
Ethical and Privacy Considerations	Transparency, fairness, and data protection compliance	4.9	Very strong agreement; users trust ethical safeguards
Usability and Integration	Ease of use, intuitiveness, and non intrusiveness during test sessions	4.7	Strong agreement; seamless integration with exam environment
Documentation and Future Development	Clarity of documentation and support for continued improvement	4.8	Strong agreement; users endorse further development and adoption
Overall Mean	Aggregate score across all categories	4.7	Excellent overall acceptance and satisfaction
## Presentation of Data Results
The study dataset contains 186 session-level observations, with 93 records in each label class. It combines heatmap-distribution features with event-log features and is interpreted as an exploratory session-level dataset.
The system generated outputs including gaze heatmaps, event-activated replay clips, and CSV session logs of gaze direction and duration. These served as the primary basis for analysis. Heatmaps displayed gaze concentration patterns, replay clips captured contextual evidence of suspicious events, and CSV logs provided quantitative measurements of gaze durations and directional shifts.
Each trial underwent an independent calibration process to align gaze coordinates with the camera’s field of view. Variations in tester height, seating distance, and facial positioning influenced detection precision. To ensure comparability, all heatmaps were manually aligned to a standardized reference screen area, preserving relative gaze distribution while compensating for calibration differences.

## Captured Video Evidence
Each session records MP4 evidence clips when a rule-based behavioral violation is triggered, including frantic eye movement, forbidden-key events, off-screen gaze, or prolonged directional gaze. Across the 186 sessions, the system captured 3,135 clips: 2,035 in label-1 sessions and 1,100 in label-0 sessions.

Label-1 sessions produced a mean of 21.88 clips per session, compared with 11.83 clips per label-0 session. The median counts were 20 and 11, respectively, while the observed ranges were 4 to 57 clips for label 1 and 1 to 38 clips for label 0. This represents a mean difference of 10.05 clips per session, or approximately 84.9% more captured clips in label-1 sessions.

The violation-category totals also differed between the label groups. Forbidden-key clips totaled 509 for label 1 and 3 for label 0; frantic-eye-movement clips totaled 992 and 768; off-screen clips totaled 132 and 38; and duration-gaze clips totaled 402 and 291, respectively. These counts describe rule-triggered events associated with the experimental labels and should not be interpreted as direct proof of academic misconduct.

A two-sample t-test found a difference in clip counts between the groups ($t = 8.44$, $p = 2.67 \times 10^{-15}$). A Mann-Whitney U test produced a similar result ($U = 7,370.5$, $p = 1.76 \times 10^{-18}$). These tests indicate a statistically significant difference in captured clip counts within this dataset, but they do not establish causal or real-world cheating-detection validity.

## Observed Feature Patterns
Label-1 sessions generally showed more active and dispersed gaze behavior than label-0 sessions. The strongest differences included approximately 260 more gaze transitions on average, approximately 5.5 more forbidden-key violations, higher heatmap coverage and entropy, a lower peak ratio, and more time spent outside the center region.

Several heatmap features were strongly correlated. Entropy and coverage ratio had an approximate correlation of 0.94, entropy and peak ratio approximately -0.92, and coverage ratio and peak ratio approximately -0.91. Because these measures describe related aspects of gaze distribution, their redundancy may reduce independent information and complicate feature-importance interpretation.

Potential outliers included an elongation ratio of approximately 39.65, up to 1,547 gaze transitions, 16 forbidden-key violations, 30 off-screen violations, and 24 duration violations in individual sessions. These values should be interpreted as possible behavior, session-length, tracking, or data-processing effects rather than removed automatically.

## Prediction-Model Results
The calibrated Random Forest baseline was evaluated using stratified five-fold cross-validation. The cross-validated accuracy was 0.909 and the ROC-AUC was 0.974. The classification report showed precision, recall, and F1-score values of approximately 0.90 to 0.91 for both label classes, with 93 sessions represented in each class.

These results describe performance within cross-validation rather than on an independent test set. They may be optimistic if sessions from the same participant or recording conditions occur in both training and validation folds, or if violation-related features are closely connected to the experimental labels. The model is therefore treated as an exploratory baseline; participant-level splitting, independent holdout testing, and evaluation with and without violation features are required before deployment claims can be made.
## Non-Cheating Heatmap Observations
The aggregated heatmap of label-0 sessions displayed a concentrated focal area near the center of the screen, indicating sustained visual attention on the examination interface. The high-intensity region reflected consistent gaze fixation, suggesting that test takers maintained focus on the active question area throughout those sessions. The observed pattern represents a dataset-level association and should not be treated as proof that every label-0 session reflects identical behavior.


Figure 32.1 Non-Cheating Heatmap
## Cheating Heatmap Observations
The heatmaps generated from label-1 sessions showed more dispersed gaze clusters across peripheral regions of the screen, characterized by multiple high intensity points rather than a single focal area. This scattered pattern indicated less concentrated visual attention, with frequent shifts away from the central exam interface. The dispersion may be consistent with multitasking or external reference checking behavior, although the dataset labels represent the experimental conditions used to construct the sessions and do not independently prove misconduct.


Figure 32.2 Cheating Heatmap
## Video Clipping System Observations
Table 16. VCS Observations
 
Clip totals and per-session averages are not used as primary outcome measures because the source video files must first be matched to their session identifiers. In the system, clips are triggered by rule-based event activations such as irregular gaze, off-screen focus, or forbidden events reported by the monitoring path.
## Gaze Direction Duration Observations
Table 17. Gaze Observations
 
Label-0 sessions maintained a more concentrated central gaze distribution, while label-1 sessions distributed gaze more evenly across multiple directions. These differences are descriptive associations within the available dataset; their statistical strength should be reported only with the corresponding session counts, raw observations, and uncertainty measures.
## Overall System Performance
Across the gaze-tracking, heatmap, event-logging, video-evidence, and prediction components, the system produced measurable differences between label-0 and label-1 sessions. Calibration differences were normalized through the documented calibration process and heatmap alignment, supporting comparison of the observed behavioral patterns. These results demonstrate prototype-level separation between the experimental labels, not definitive real-world cheating detection.
## Data Interpretation
The combined findings from the heatmap, clip-count, gaze-duration, event-log, and prediction analyses indicate measurable differences between the label-0 and label-1 sessions. The concentrated gaze patterns in label-0 sessions are consistent with more focused engagement, while the scattered attention and higher violation-clip counts in label-1 sessions indicate more dispersed or eventful behavior. These findings demonstrate the system’s ability to produce distinguishable behavioral indicators within the study dataset, rather than validating autonomous cheating detection.

These observations are consistent with the initial hypothesis that legitimate test-taking behavior may produce more concentrated attention near the exam interface, whereas simulated use of external resources may produce more dispersed gaze patterns. The quantitative differences are exploratory associations within controlled trials and do not provide conclusive evidence that the computer-vision modules can reliably identify real-world cheating.

However, the researchers also recognize the overlap between normal and cheating behaviors, such as brief glances away or posture adjustments, which may lead to false positives if interpreted without context. This reinforces the study’s central argument that detection systems should function as assistive tools for human proctors, not as autonomous arbiters of integrity. By providing structured behavioral data, which includes heatmaps, clip counts, and gaze metrics, the system empowers proctors to make informed, evidence based decisions supported by visual and quantitative indicators.
Overall, the synthesis indicates that the MAKITEST prototype produces interpretable behavioral outputs that may assist human review. The findings do not establish conclusive real-world cheating detection; further participant-level validation, independent testing, and documented data lineage are required before stronger claims about fairness, reliability, or deployment suitability can be made.
# Chapter 5: Conclusion
## Summary of Findings
The evaluation showed that the gaze-tracking prototype produced measurable patterns of attention and distraction during controlled examination trials. The system uses calibrated gaze-direction thresholds, head-pose estimates, iris-based eye position, event logs, and heatmap features to describe behavior. In the reported simulations, non-cheating and simulated cheating sessions showed different gaze distributions; however, these observations do not establish consistent real-world cheating-detection accuracy. The dual-component gaze-estimation architecture provides behavioral indicators that may support proctor decision-making, subject to the limitations of calibration, hardware, sample size, and ground-truth labeling.
## Conclusions
The study developed a prototype Suspicious Exam Behavior Detection System (SEBDS) centered on gaze tracking and head-pose estimation. By integrating these modalities with rule-based event scoring and session-level feature extraction, the system provides a more descriptive view of examinee behavior than a single binary movement rule. The current evidence supports the feasibility of using these outputs as proctor-assistance data, but it does not demonstrate that the system minimizes false positives or reliably detects real-world cheating. Those conclusions require independent participant-level validation and a documented evaluation dataset.
## Contributions
This research contributed a calibrated gaze tracking framework and dataset that is tailored for academic assessment environments. It established measurable parameters for gaze duration, direction, and deviation thresholds, which form the basis for behavioral scoring. The study also documented the calibration protocol and evaluation metrics that ensure reproducibility. By focusing on visual attention analysis rather than restrictive lockdown mechanisms, the project advances ethical and human centered approaches to exam monitoring. The resulting dataset and detection logic provide future researchers with a benchmark for refining gaze based integrity systems.
## Limitations
The evaluation was conducted under controlled conditions with limited hardware diversity and lighting variations, which restricts generalizability. The implemented detection system focuses on iris-based gaze estimation, head pose, browser or keyboard events, heatmap generation, and rule-based scoring; hand tracking, object detection, facial recognition, liveness detection, and sound analysis are not implemented. Accuracy depends on camera positioning, calibration, image quality, frame rate, and the distinction between simulated conditions and real-world misconduct. The web app integration is a prototype and is not optimized for large-scale deployment. The current dataset also requires participant-level splitting, independent holdout testing, and investigation of possible label leakage before deployment claims can be supported.
## Recommendations
Future research should expand the gaze tracking dataset to include diverse lighting conditions, facial orientations, and camera types. Additional behavioral cues such as object detection and keystroke dynamics should be integrated to provide richer context. Adaptive calibration models that automatically adjust thresholds per user session are recommended to enhance precision. Cross institutional testing is also necessary to refine detection accuracy and minimize environmental bias. Continued development and improvement of the web app integration are essential for achieving seamless operation under real world exam conditions. This includes enhancing interface responsiveness, strengthening privacy safeguards through encryption and secure data storage policies, and ensuring compatibility with institutional systems. Real time visualization tools where proctors can interpret gaze data more intuitively should also be explored to support informed decision making during examinations.
## Final statement
In conclusion, the MAKITEST project demonstrated the feasibility of combining calibrated gaze estimation, head-pose analysis, browser or keyboard events, heatmaps, and session-level prediction in a proctor-assistance prototype. Controlled trials produced behavioral differences between non-cheating and simulated cheating conditions, but those differences should be treated as exploratory indicators rather than proof of misconduct. The Django web integration establishes a pathway for browser-based examination monitoring, while further work is needed to reconcile dataset versions, validate the classifier on independent participants and sessions, improve calibration robustness, and document privacy and deployment safeguards.
## References
Adzima, K. (2021). Examining online cheating in higher education using traditional classroom cheating as a guide. The Electronic Journal of e-Learning, 18(6). https://doi.org/10.34190/jel.18.6.002
Al-Maqbali, A., & Hussain, R. M. R. (2022). The impact of online assessment challenges on assessment principles during COVID-19 in Oman. Journal of University Teaching and Learning Practice, 19(2), 73–92. https://doi.org/10.53761/1.19.2.6
Armstrong-Mensah, E., Ramsey-White, K., Yankey, B., & Self-Brown, S. (2020). COVID-19 and distance learning: Effects on Georgia State University School of Public Health Students. Frontiers in Public Health, 8, 576227. https://doi.org/10.3389/fpubh.2020.576227
Barnes, C., & Paris, B. L. (2013). AN ANALYSIS OF ACADEMIC INTEGRITY TECHNIQUES USED IN ONLINE COURSES AT A SOUTHERN UNIVERSITY. In Lamar University, Research Gate [Journal-article]. https://www.researchgate.net/publication/264000798_AN_ANALYSIS_OF_ACADEMIC_INTEGRITY_TECHNIQUES_USED_IN_ONLINE_COURSES_AT_A_SOUTHERN_UNIVERSITY
Batool, H., Mumtaz, A., Ali, S., & A.S. Chughtai. (2018). Positive trend Shifting to online assessments: A review of using Socrative in Medical College, Its advantages and Challenges faced. In Journal of Medical Education (Vols. 3–3, pp. 160–167).
Bawarith, R., Abdullah, & Anas. (2017). E-Exam Cheating Detection System. International Journal of Advanced Computer Science and Applications, 8(4). https://doi.org/10.14569/ijacsa.2017.080425
Benson, L., & Enstroem, R. (2023). A model for preventing academic misconduct: evidence from a large-scale intervention. International Journal for Educational Integrity, 19(1). https://doi.org/10.1007/s40979-023-00147-y
Bilen, E., & Matros, A. (2020). Online cheating amid COVID-19. Journal of Economic Behavior & Organization, 182, 196–211. https://doi.org/10.1016/j.jebo.2020.12.004
Breskina, A. A. (2023). Development of an automated online proctoring system. Herald of Advanced Information Technology, 6(2), 163–173. https://doi.org/10.15276/hait.06.2023.11
Bretag, T., Harper, R., Burton, M., Ellis, C., Newton, P., Rozenberg, P., Saddiqui, S., & Van Haeringen, K. (2018). Contract cheating: a survey of Australian university students. Studies in Higher Education, 44(11), 1837–1856. https://doi.org/10.1080/03075079.2018.1462788
BurnahAcc123. (2024). I get to question 57/65, now they stop my exam for “behavioural” reasons, they wont tell me what I did exactly.  Asks me to show my room. This was a super tedious process - I had to show multiple positions and hold the camera a certain way for a certain amount of time, I complied. Then the proctor tells me it’s not sufficient and to do it all over again. Reddit. https://www.reddit.com/r/salesforce/comments/1bgwfh1/flipped_off_the_kryterion_online_proctor_after/
Carrasco, M. (2022, January 28). Instructors express fewer concerns about online cheating. Inside Higher Ed | Higher Education News, Events and Jobs. https://www.insidehighered.com/news/2022/01/28/instructors-express-fewer-concerns-about-online-cheating
Carreira, J., & Zisserman, A. (2017, July 1). Quo Vadis, Action Recognition? A New Model and the Kinetics Dataset. https://doi.org/10.1109/cvpr.2017.502
Cerimagic, S., & Hasan, M. R. (2019). Online exam vigilantes at Australian Universities: student academic fraudulence and the role of universities to Counteract. Universal Journal of Educational Research, 7(4), 929–936. https://doi.org/10.13189/ujer.2019.070403
Chadaga, N. (2025, February 10). How candidates use technology to cheat in online technical assessments. Hackerearth. https://www.hackerearth.com/blog/different-ways-candidates-cheat-in-online-technical-assessments
Cluskey, G. R., Jr., Troy University, Global Campus, Ehlen, C. R., University of Southern Indiana, Raiborn, M. H., & Bradley University. (n.d.). Thwarting online exam cheating without proctor supervision. In Journal of Academic and Business Ethics (p. 1). http://www.aabri.com/manuscripts/11775.pdf
Comas-Forgas, R., Lancaster, T., Calvo-Sastre, A., & Sureda-Negre, J. (2021). Exam cheating and academic integrity breaches during the COVID-19 pandemic: An analysis of internet search activity in Spain. Heliyon, 7(10), e08233. https://doi.org/10.1016/j.heliyon.2021.e08233
Culver, C. (2024, April 11). More Research Shows that Cheating is More Common in Online Environments. The Cheat Sheet. https://thecheatsheet.substack.com/p/more-research-shows-that-cheating
Curtis, K. (2023, November 6). Cheating & Plagiarism in Online School: Awareness & Prevention. Public Service Degrees. https://www.publicservicedegrees.org/college-resources/cheating-plagiarism-prevention/
Danielsen, N. F., Gravdal, P. K., & NTNU – Norwegian University of Science and Technology. (2020). Detecting Contract Cheating by using Stylometry and Keystroke Dynamics. In NTNU – Norwegian University of Science and Technology.
Dawson, P. (2020). Defending assessment security in a digital world (1st ed.). https://doi.org/10.4324/9780429324178
Deleted User. (2022). Be warned that the online-proctored experience with Kryterion has been horrible for me. [Comment on “Kryterion Online Exam - Terrible”]. https://www.reddit.com/r/GCPCertification/comments/vyt3rs/kryterion_online_exam_terrible/
Dendir, S., & Maxwell, R. S. (2020). Cheating in online courses: Evidence from online proctoring. Computers in Human Behavior Reports, 2, 100033. https://doi.org/10.1016/j.chbr.2020.100033
Derakhshan, A., & Shakki, F. (2024). Opportunities and challenges of implementing online English courses in Iranian public and private schools [Research Paper]. Journal of Research in Applied Linguistics, 1, 17–31. https://doi.org/10.22055/rals.2023.44418.3111
Dilini, N., Senaratne, A., Yasarathna, T., Warnajith, N., & Seneviratne, L. (2021). Cheating Detection in Browser-based Online Exams through Eye Gaze Tracking. 2021 6th International Conference on Information Technology Research (ICITR), 1–8. https://doi.org/10.1109/icitr54349.2021.9657277
Dimeo, J. (2017, May 10). Online exam proctoring catches cheaters, raises concerns. Inside Higher Ed | Higher Education News, Events and Jobs. https://www.insidehighered.com/digital-learning/article/2017/05/10/online-exam-proctoring-catches-cheaters-raises-concerns
Elsalem, L., Al-Azzam, N., Jum’ah, A. A., & Obeidat, N. (2021). Remote E-exams during Covid-19 pandemic: A cross-sectional study of students’ preferences and academic dishonesty in faculties of medical sciences. Annals of Medicine and Surgery, 62, 326–333. https://doi.org/10.1016/j.amsu.2021.01.054
ExaminationSweaty926. (2025, September). I can’t start my Google Cloud Online Exam due to LockDown Browser’s issue. I’m pretty sure: I didn’t install it [Comment on “Ridiculous experience with kryterion’s support team during google cloud Online Proctored Exam”]. https://www.reddit.com/r/cybersecurity_help/comments/1n972si/ridiculous_experience_with_kryterions_support/
Fagell, P. L. (2020). Career Confidential: Teacher wonders how to help students during coronavirus shutdown. Phi Delta Kappan, 101(8), 67–68. https://doi.org/10.1177/0031721720923799
Fluck, A. E. (2018). An international review of eExam technologies and impact. Computers & Education, 132, 1–15. https://doi.org/10.1016/j.compedu.2018.12.008
Foster, D., Caveon Test Security, Layman, H., & The College Board. (2013). Online proctoring systems compared. https://ivetriedthat.com/wp-content/uploads/2014/07/Caveon-Test-Security.pdf
Gamage, K. A., De Silva, E. K., & Gunawardhana, N. (2020). Online Delivery and Assessment during COVID-19: Safeguarding Academic Integrity. Education Sciences, 10(11), 301. https://doi.org/10.3390/educsci10110301
Garg, M., & Goel, A. (2021). A systematic literature review on online assessment security: Current challenges and integrity strategies. Computers & Security, 113, 102544. https://doi.org/10.1016/j.cose.2021.102544
Garg, M., & Goel, A. (2023). Detection of internet cheating in online assessments using cluster analysis. In Lecture notes in networks and systems (pp. 77–90). https://doi.org/10.1007/978-981-99-1414-2_7
Goff, D., Johnston, J., & Bouboulis, B. (2020). Maintaining academic standards and integrity in online business courses. International Journal of Higher Education, 9(2), 248. https://doi.org/10.5430/ijhe.v9n2p248
Gonzales, R. D. (2023). From Face-to-Face to Virtual Student Assessment: Changes in Student Assessment Practices during COVID-19 Among Filipino Teachers. European Journal of Education and Pedagogy, 4(1), 159–164. https://doi.org/10.24018/ejedu.2023.4.1.579
Harmon, O. R., Lambrinos, J., Department of Economics Working Paper Series, University of Connecticut, & Union University. (2006). Are online exams an invitation to cheat? In Department of Economics Working Paper Series (Report No. 2006-08R). http://www.econ.uconn.edu/
Harton, H. C., Aladia, S., & Gordon, A. (2019). Faculty and student perceptions of cheating in online vs. traditional classes. Online Journal of Distance Learning Administration, 22(4). https://ojdla.com/archive/winter224/hartonaladiagordon224.pdf
Hasri, A., Supar, R., Azman, N. D. N., Sharip, H., & Yamin, L. S. M. (2022). Students’ Attitudes and Behavior towards Academic Dishonesty during Online Learning. International Academic Symposium of Social Science 2022, 36. https://doi.org/10.3390/proceedings2022082036
Holden, O. L., Norris, M. E., & Kuhlmeier, V. A. (2021). Academic Integrity in Online Assessment: A Research review. Frontiers in Education, 6. https://doi.org/10.3389/feduc.2021.639814
Hu, Z., Jing, Y., Wu, G., & Wang, H. (2024). Multi-Perspective Adaptive Paperless Examination cheating detection system based on image recognition. Applied Sciences, 14(10), 4048. https://doi.org/10.3390/app14104048
Hussein, M. J., Yusuf, J., Deb, A. S., Fong, L., & Naidu, S. (2020). An evaluation of online proctoring tools. Open Praxis, 12(4), 509. https://doi.org/10.5944/openpraxis.12.4.1113
Hylton, K., Levy, Y., & Dringus, L. P. (2015). Utilizing webcam-based proctoring to deter misconduct in online exams. Computers & Education, 92–93, 53–63. https://doi.org/10.1016/j.compedu.2015.10.002
Jalilzadeh, K., Rashtchi, M., & Mirzapour, F. (2024). Cheating in online assessment: a qualitative study on reasons and coping strategies focusing on EFL teachers’ perceptions. Language Testing in Asia, 14(1). https://doi.org/10.1186/s40468-024-00304-1
Janison. (2025, October 12). 6 ways students cheat online assessments, and how to stop them. Janison Solutions Pty Ltd. https://www.janison.com/resources/post/6-common-ways-students-cheat-at-online-assessments/
Janke, S., Rudert, S. C., Petersen, Ä., Fritz, T. M., & Daumiller, M. (2021). Cheating in the wake of COVID-19: How dangerous is ad-hoc online testing for academic integrity? Computers and Education Open, 2, 100055. https://doi.org/10.1016/j.caeo.2021.100055
Jordan, A. E. (2001). College Student cheating: the role of motivation, perceived norms, attitudes, and knowledge of institutional policy. Ethics & Behavior, 11(3), 233–247. https://doi.org/10.1207/s15327019eb1103_3
Lancaster, T. (2021). Academic dishonesty or academic integrity? Using natural language processing (NLP) techniques to investigate positive integrity in academic integrity research. Journal of Academic Ethics, 19(3), 363–383. https://doi.org/10.1007/s10805-021-09422-4
Lancaster, T., & Cotarlan, C. (2021). Contract cheating by STEM students through a file sharing website: a Covid-19 pandemic perspective. International Journal for Educational Integrity, 17(1). https://doi.org/10.1007/s40979-021-00070-0
Liang, J. G., Watson, G. R., Sottile, J., & Behrend, B. A. (2023). Academic cheating in online and live college courses during the COVID pandemic. In Journal of Research in Education (Vol. 32, Issue 2, pp. 96–98). https://files.eric.ed.gov/fulltext/EJ1412003.pdf
Lupton, A. (2020, October 15). Western students alerted about security breach at exam monitor Proctortrack. CBC. https://www.cbc.ca/news/canada/london/western-students-alerted-about-security-breach-at-exam-monitor-proctortrack-1.5764354
Malik, A. A., Hassan, M., Rizwan, M., Mushtaque, I., Lak, T. A., & Hussain, M. (2023). Impact of academic cheating and perceived online learning effectiveness on academic performance during the COVID-19 pandemic among Pakistani students. Frontiers in Psychology, 14, 1124095. https://doi.org/10.3389/fpsyg.2023.1124095
Marano, E., Newton, P. M., Birch, Z., Croombs, M., Gilbert, C., & Draper, M. J. (2024). What is the student experience of remote proctoring? A pragmatic scoping review. Higher Education Quarterly, 78(3), 1031–1047. https://doi.org/10.1111/hequ.12506
Matsumoto, Y., Zelinsky, A., Nara Institute of Science and Technology, & The Australian National University. (2000). An algorithm for real-time stereo vision implementation of head pose and gaze direction measurement. Proceedings Fourth IEEE International Conference on Automatic Face and Gesture Recognition (Cat. No. PR00580). https://users.cecs.anu.edu.au/~rsl/rsl_papers/FG2000.pdf
Moralista, R. B., & Oducado, R. M. F. (2020). Faculty Perception toward Online Education in a State College in the Philippines during the Coronavirus Disease 19 (COVID-19) Pandemic. Universal Journal of Educational Research, 8(10), 4736–4742. https://doi.org/10.13189/ujer.2020.081044
Moten, J., Jr, Fitterer, A., Brazier, E., Leonard, J., & Brown, A. (2013, June 1). Examining online college cyber cheating methods and prevention measures. https://academic-publishing.org/index.php/ejel/article/view/1664
Newton, P. M., & Essex, K. (2023). How Common is Cheating in Online Exams and did it Increase During the COVID-19 Pandemic? A Systematic Review. Journal of Academic Ethics, 22(2), 323–343. https://doi.org/10.1007/s10805-023-09485-5
Noorbehbahani, F., Mohammadi, A., & Aminazadeh, M. (2022). A systematic review of research on cheating in online exams from 2010 to 2021. Education and Information Technologies, 27(6), 8413–8460. https://doi.org/10.1007/s10639-022-10927-7
Omer, T. (2022, August 17). 10 ways to cheat on online exams (and 9 ways to prevent it). BrightLink Prep. https://brightlinkprep.com/ways-to-cheat-on-online-exams/
On knuckle scanners and cheating – How to bypass Proctortrack, Examity, and the rest | Jake Binstein. (n.d.). https://jakebinstein.com/blog/on-knuckle-scanners-and-cheating-how-to-bypass-proctortrack
Oravec, J. A. (2022). AI, biometric analysis, and emerging cheating detection systems: The engineering of academic integrity? Education Policy Analysis Archives, 30. https://doi.org/10.14507/epaa.30.5765
Pang, D., Wang, T., Ge, D., Zhang, F., & Chen, J. (2022). RETRACTED ARTICLE: How to help teachers deal with students’ cheating in Online Examinations: Design and Implementation of International Chinese Online Teaching Test Anti-Cheating Monitoring System (OICIE-ACS). Electronic Commerce Research, 24(S1), 7–8. https://doi.org/10.1007/s10660-022-09649-2
Percival, N., Percival, J., & Martin, C. (2008). The Virtual Invigilator: A Network-based Security System for Technology-enhanced Assessments. In Proceedings of the World Congress on Engineering and Computer Science 2008, Proceedings of the World Congress on Engineering and Computer Science 2008 [Conference-proceeding]. https://www.researchgate.net/publication/44262368_The_Virtual_Invigilator_A_Network-based_Security_System_for_Technology-enhanced_Assessments
Podio, F. L., & Dunn, J. S. (2001). Biometric Authentication Technology: From the Movies to Your Desktop. Journal of Research of NIST. https://www.nist.gov/publications/biometric-authentication-technology-movies-your-desktop
Rettinger, D. A., & Kramer, Y. (2008). Situational and personal causes of student cheating. Research in Higher Education, 50(3), 293–313. https://doi.org/10.1007/s11162-008-9116-5
Rogers, C. (2006). Faculty perceptions about e-cheating during online testing. Journal of Computing Sciences in College, 22, 206–212. https://www.researchgate.net/publication/262311152_Faculty_perceptions_about_e-cheating_during_online_testing
Samir, M. A., Maged, Y., & Atia, A. (2021). Exam Cheating Detection System with Multiple-Human Pose Estimation. 2021 IEEE International Conference on Computing (ICOCO), 236–240. https://doi.org/10.1109/icoco53166.2021.9673534
Sevnarayan, K., & Maphoto, K. B. (2024). Exploring the dark side of online distance learning: cheating behaviours, contributing factors, and strategies to enhance the integrity of online assessment. Journal of Academic Ethics, 22(1), 51–70. https://doi.org/10.1007/s10805-023-09501-8
Slusky, L. (2020). Cybersecurity of online proctoring systems. Journal of International Technology and Information Management, 29(1), 56–83. https://doi.org/10.58729/1941-6679.1445
Stuber-McEwen, D., Wiseley, P., & Hoggatt, S. (2009). Point, click, and cheat: Frequency and type of academic dishonesty in the virtual classroom. Online Journal of Distance Learning Administration, 12(3). http://www.itcnetwork.org/resources/268-point-click-and-cheat-frequency-and-type-of-academic-dishonesty-in-the-virtual-classroom.pdf
The realities of cheating in online classes & exams. (2023, August 25). https://www.onlineeducation.com/features/cheating-in-online-education
Valizadeh, M. (2022). CHEATING IN ONLINE LEARNING PROGRAMS: LEARNERS’ PERCEPTIONS AND SOLUTIONS. Turkish Online Journal of Distance Education, 23(1), 195–209. https://doi.org/10.17718/tojde.1050394
Valverde-Berrocoso, J., Del Carmen Garrido-Arroyo, M., Burgos-Videla, C., & Morales-Cevallos, M. B. (2020). Trends in Educational Research about e-Learning: A Systematic Literature Review (2009–2018). Sustainability, 12(12), 5153. https://doi.org/10.3390/su12125153
Varble, D. & Indiana State University. (2014). Reducing cheating opportunities in online test. In Atlantic Marketing Journal (p. Article 9). https://digitalcommons.kennesaw.edu/amj/vol3/iss3/9
Vellanki, S. S., Mond, S., & Khan, Z. K. (2023). Promoting Academic Integrity in Remote/Online Assessment – EFL Teachers’ Perspectives. Teaching English as a Second or Foreign Language--TESL-EJ, 26(4), 1–20. https://doi.org/10.55593/ej.26104a7
Walsh, L. L., Lichti, D. A., Zambrano-Varghese, C. M., Borgaonkar, A. D., Sodhi, J. S., Moon, S., Wester, E. R., & Callis-Duehl, K. L. (2021). Why and how science students in the United States think their peers cheat more frequently online: perspectives during the COVID-19 pandemic. International Journal for Educational Integrity, 17(1). https://doi.org/10.1007/s40979-021-00089-3
Zarzycka, E., Krasodomska, J., Mazurczak-Mąka, A., & Turek-Radwan, M. (2021). Distance learning during the COVID-19 pandemic: students’ communication and collaboration and the role of social media. Cogent Arts and Humanities, 8(1). https://doi.org/10.1080/23311983.2021.1953228
Zhao, J., Awais-E-Yazdan, M., Mushtaque, I., & Deng, L. (2022). The Impact of technology adaptation on academic engagement: A moderating role of perceived argumentation strength and school support. Frontiers in Psychology, 13, 962081. https://doi.org/10.3389/fpsyg.2022.962081
Zhao, Q., & Ye, M. (2010). The application and implementation of face recognition in authentication system for distance education. 2010 International Conference on Networking and Digital Society, 25, 487–489. https://doi.org/10.1109/icnds.2010.5479246













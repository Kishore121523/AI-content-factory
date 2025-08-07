from typing import Optional

#Builds SSML documents for Azure TTS
class SSMLBuilder:
    
    def __init__(self, style_manager, script_processor):
        self.style_manager = style_manager
        self.script_processor = script_processor
    
    #Create SSML document with voice and style with degree control
    def create_ssml(self, text: str, voice_name: str, style: str, 
                    emotion: Optional[str] = None) -> str:
        # Clean text for XML
        clean_text = self.script_processor.escape_xml_text(text)
        
        # Get style degree if emotion provided
        style_degree_attr = ""
        if emotion:
            degree = self.style_manager.get_style_degree(emotion)
            if degree != 1.0:
                style_degree_attr = f' styledegree="{degree}"'
        
        # Create SSML with style degree
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
                    <voice name="{voice_name}">
                        <mstts:express-as style="{style}"{style_degree_attr}>
                            {clean_text}
                        </mstts:express-as>
                    </voice>
                </speak>"""
        
        return ssml
	function copyToClipboard(element, id) {
									        textRange = $(id);
									        
									        textRange.html(element)
									        //$(textRange).focus()
									        $(textRange).select();
									        document.execCommand("Copy");
									   			 }


	$(document).ready(function() {
		
		
		$("#CRTYPE").click(function() {
			Resultat = "{{page}}".indexOf("radio");
			if (Resultat != -1)//si on  est sur une page radio
			{compteRenduType = "Relecture de radiographies pour les urgences\n\n" + compteRenduType.replace(/xx/g,"\n")}
			else
			{compteRenduType = compteRenduType.replace(/xx/g,"\n")}
			
			copyToClipboard(compteRenduType, id="#textarea");
  			   			 					
				

		} );

				});

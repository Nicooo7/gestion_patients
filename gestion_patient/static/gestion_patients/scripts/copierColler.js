	function copyToClipboard(element, id) {
									        textRange = $(id);
									        
									        textRange.html(element)
									        //$(textRange).focus()
									        $(textRange).select();
									        document.execCommand("Copy");
									   			 }


	$(document).ready(function() {
		
		
		$("#CRTYPE").click(function() {

			compteRenduType = "Relecture de radiographies pour les urgences\n\n" + compteRenduType.replace(/xx/g,"\n")
			copyToClipboard(compteRenduType, id="#textarea");
  			   			 					
				

		} );

				});

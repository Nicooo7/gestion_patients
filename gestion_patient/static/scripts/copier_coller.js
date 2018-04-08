	function copyToClipboard(element, id) {
									        textRange = $(id);
									        
									        textRange.html(element)
									        //$(textRange).focus()
									        $(textRange).select();
									        document.execCommand("Copy");
									   			 }


	$(document).ready(function() {
		
		
		$("#CRTYPE").click(function() {

			compteRenduType = compteRenduType.replace(/xx/g,"\n")
			copyToClipboard(compteRenduType, id="#textarea");
  			   			 					
				

		} );

				});

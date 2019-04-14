<?php

/* documentation:
==========================

written by: M. Riedel, 2018

The script aims to create a DublinCoreXML for each data collections published (DIP).
Each XMl-file collects the metadata of one single data collection, defined as package.
The XML were created as an exchange format in order to list the IANUS data packages
in the Deutsche Digitale Bibliothek (DDB). Unfortunately, the data model of IANUS and
the data model of the DDB did not fit together, so the packages haven´t been listed yet.


/* database connection:
=========================*/
	
$host = "localhost";								
$user = "root";
$password = "";
$database = "ianus";

$mysql = new mysqli($host, $user, $password, $database);		
	
mysqli_set_charset($mysql, "utf8");								

if ($mysql->connect_errno) {
	
	$error_message = "Fehler: ".mysqli_connect_error();
	
};

/* query DIPs:
==================*/

$query = "SELECT * FROM disseminationIP DIP
		  WHERE DIP.state LIKE 'Finished';";	  
 
$result = $mysql->query($query);	

// get metadataId from result:
echo "Prozessierte DIPs:<br><br>";

while($data = $result->fetch_assoc()) {		

	$metadataId = $data["metadataId"];
	$metadataIDs[] = $metadataId;
	
	// logging:
	$collectionLabel = $data["collectionLabel"];
	
	echo $metadataId." - ".$collectionLabel."<br>";
};

/* get metadata of each collection by metadataId:
===================================================*/

foreach($metadataIDs as $metadataId) {
	
	/* get format as dcterms:extent (of collection)
	----------------------------------------------*/
	$query = "SELECT memorySize FROM ianus_metadata.datacollection WHERE id = $metadataId;";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$value = $data["memorySize"];	// in some cases = NULL
		
		$mapping_data[$metadataId]["format"][] = $value;

	};
	
	/* get DC:rights as license from datacollection
	-----------------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.datacollection WHERE id = $metadataId;";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$value = $data["licenseName"]. " ". $data["licenseVersion"];
		
		$mapping_data[$metadataId]["rights"][] = $value;

	};
	
	/* get DC:date from datacollection:
	-----------------------------------*/
	$query = "SELECT * FROM ianus_metadata.datacollection WHERE id = $metadataId;";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$date_issued = explode(" ", $data["presentationDate"]);	// cut of time: 00:00:00
		
		$mapping_data[$metadataId]["date_issued"][] = $date_issued[0];
	};
	
		
	/* get DC:identifier from identifier
	--------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.identifier WHERE sourceId = $metadataId AND (type = 'dcms_DOI' OR type = 'dcms_URL' OR type = 'dcms_Handle');";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$type = $data["type"];
		
		if($type == "dcms_DOI") {
			
			$value = $data["value"];
		}
		else {
			$value = $data["uri"];
		};
		
		$mapping_data[$metadataId]["identifier"][$type] = $value;	
	};


	/* get DC:subject from elementoflist:
	--------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.elementoflist WHERE (contentType NOT LIKE 'dataCategory' AND contentType NOT LIKE 'classification') AND sourceId = $metadataId";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$value = $data["value"];
	
		$mapping_data[$metadataId]["subject"][] = $value;
	};
	
	
	/* get DC:coverage from time and place (join elementoflist):
	-------------------------------------------------------------*/
	
	// time:
	$query = "SELECT * FROM ianus_metadata.time JOIN ianus_metadata.elementoflist ON time.id = elementoflist.sourceId WHERE time.sourceId = $metadataId";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$value = $data["value"];
	
		$mapping_data[$metadataId]["coverage"]["temporal"][] = $value;
	};
	
	// place:
	$query = "SELECT * FROM ianus_metadata.place JOIN ianus_metadata.elementoflist ON place.id = elementoflist.sourceId WHERE place.sourceId = $metadataId";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$value = $data["value"];
	
		$mapping_data[$metadataId]["coverage"]["spatial"][] = $value;
	};
	
	
	/* get DC:type from elementoflist:
	-----------------------------------*/
	$query = "SELECT * FROM ianus_metadata.elementoflist WHERE sourceId = $metadataId AND (contentType LIKE 'dataCategory' OR contentType LIKE 'classification')";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$value = $data["value"];
	
		$mapping_data[$metadataId]["type"][] = $value;
	};
	
	/* get DC:title from textattribute
	--------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.textattribute WHERE sourceId = $metadataId AND contentType = 'title';";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$value = $data["value"];
		$languageCode = $data["languageCode"];
		
		$mapping_data[$metadataId]["title"][$languageCode] = $value;	
	};
	
	/* get DC:description from textattribute:
	------------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.textattribute WHERE sourceId = $metadataId;";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$value = $data["value"];
		$contentType = $data["contentType"];
		$languageCode = $data["languageCode"];
		
		$mapping_data[$metadataId]["description"][$languageCode] = $value;
	};
	
	/* get DC:creator from person:
	------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.actorrole JOIN ianus_metadata.person WHERE person.sourceId = $metadataId AND person.id = actorrole.actorId AND actorrole.typeId LIKE 'ianus_PrincipalInvest'";
	
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$person = $data["firstName"]." ".$data["lastName"];
	
		$mapping_data[$metadataId]["creator"][] = $person;
		
	};
	
	/* get DC:contributor from person:
	------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.person WHERE sourceId = $metadataId;";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$person = $data["firstName"]." ".$data["lastName"];
	
		$mapping_data[$metadataId]["contributor"][] = $person;
		
	};
	
	/* get DC:publisher from institution:
	--------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.actorrole JOIN ianus_metadata.institution WHERE institution.sourceId = $metadataId AND institution.id = actorrole.actorId AND actorrole.typeId LIKE 'dcms_HostingInstitution'";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$publisher = $data["name"];
	
		$mapping_data[$metadataId]["publisher"][] = $publisher;
	};

	/* get DC:language from language:
	------------------------------------*/
	$query = "SELECT * FROM ianus_metadata.language WHERE sourceId = $metadataId;";
	$result = $mysql->query($query);
	
	while($data = $result->fetch_assoc()) {
		
		$language = $data["code"];
		$contentType = $data["contentType"]; // e.g. collection_language or metadata_language
	
		$mapping_data[$metadataId]["language"][$contentType] = $language;
		
	};

};

/* output data:
=======================*/

echo "<br>Metadaten:<br><br>";
print_r($mapping_data);


/* create DC elements:
=======================*/

foreach($mapping_data as $metadataId => $collection) {
	
	// dc:identifier:
	foreach($collection["identifier"] as $type => $element) {
		
		$identifiers[] = "<dc:identifier xsi:type ='$type'>".$collection["identifier"][$type]."</dc:identifier>"; 
		$dc_identifier =  implode(PHP_EOL, $identifiers);
	};
	
	
	// dc:format as dcterms:extent:
	foreach($collection["format"] as $element) {
		
		if($element !== "") {
			
			$formats[] = "<dcterms:extent>".$element."</dcterms:extent>"; 
			$dc_format =  implode(PHP_EOL, $formats);
		};
	};
	
	// dc:type:
	$types[] = "<dc:type xsi:type='dcterms:DCMIType'>Collection</dc:type>";	 // general type term from the DCMIType vocabulary
	
	foreach($collection["type"] as $element) {
		
		$types[] = "<dc:type>".$element."</dc:type>"; 
		$dc_type =  implode(PHP_EOL, $types);
	};
	
	// dc:language:
	if(isset($collection["language"])) {
		
		foreach($collection["language"] as $contentType => $element) {
		
			$languages[] = "<dc:language>".$collection["language"][$contentType]."</dc:language>"; 
			$dc_language =  implode(PHP_EOL, $languages);
		
		};
	
	}
	else {
		
		$languages[] = "<dc:language>-</dc:language>";
		$dc_language =  implode(PHP_EOL, $languages);
	};
	
	
	// dc:title:
	foreach($collection["title"] as $languageCode => $element) {
		
		$titles[] = "<dc:title xml:lang ='$languageCode'>".$collection["title"][$languageCode]."</dc:title>"; 
		$dc_title =  implode(PHP_EOL, $titles); 	// PHP_EOL, constant for lb;
	};
	
	// dc:subject:
	foreach($collection["subject"] as $element) {	
	
		$subjects[] = "<dc:subject>".$element."</dc:subject>"; 
		$dc_subject =  implode(PHP_EOL, $subjects);
	};
	
	// dc:description:
	foreach($collection["description"] as $languageCode => $element) {
		$descriptions[] = "<dc:description xml:lang ='$languageCode'>".$collection["description"][$languageCode]."</dc:description>"; 
		$dc_description =  implode(PHP_EOL, $descriptions); 	// PHP_EOL, constant for lb;
	};
	
	// dc:coverage (dcterms:temporal)
	foreach($collection["coverage"]["temporal"] as $element) {	
		
		$temporals[] = "<dcterms:temporal>".$element."</dcterms:temporal>"; 
		$dcterms_temporal =  implode(PHP_EOL, $temporals); 
	};
	
	// dc:coverage (dcterms:spatial)
	foreach($collection["coverage"]["spatial"] as $element) {	
		
		$spatials[] = "<dcterms:spatial>".$element."</dcterms:spatial>"; 
		$dcterms_spatial =  implode(PHP_EOL, $spatials); 
	};
	
	
	// dc:creator:
	foreach($collection["creator"] as $element) {	
	
		$creators[] = "<dc:creator>".$element."</dc:creator>"; 
		$dc_creator =  implode(PHP_EOL, $creators);
	};
	
	// dc:contributor:
	foreach($collection["contributor"] as $element) {	
	
		$contributors[] = "<dc:contributor>".$element."</dc:contributor>"; 
		$dc_contributor =  implode(PHP_EOL, $contributors);
	};
	
	// dc:publisher:
	foreach($collection["publisher"] as $element) {	
	
		$publishers[] = "<dc:publisher>".$element."</dc:publisher>"; 
		$dc_publisher =  implode(PHP_EOL, $publishers);
	};

	// dc:rights:
	foreach($collection["rights"] as $element) {	
	
		$rights[] = "<dc:rights>".$element."</dc:rights>"; 
		$dc_rights =  implode(PHP_EOL, $rights);
	};
	
	// dc:date as dcterms:issued:
	foreach($collection["date_issued"] as $element) {

		$dates[] = "<dcterms:issued xsi:type = 'dcterms:W3CDTF'>".$element."</dcterms:issued>"; 
		$dc_date =  implode(PHP_EOL, $dates);
	};
	

	/* merge dc-elements together as $content:
	--------------------------------------------*/
	$content = "<package>". PHP_EOL .$dc_identifier. PHP_EOL .$dc_format. PHP_EOL .$dc_title. PHP_EOL .$dc_subject. PHP_EOL .$dc_type. PHP_EOL .$dc_description. 
				PHP_EOL . $dcterms_temporal . PHP_EOL . $dcterms_spatial . PHP_EOL .$dc_creator. PHP_EOL . $dc_contributor. PHP_EOL .$dc_publisher. PHP_EOL .$dc_language. 
				PHP_EOL .$dc_rights. PHP_EOL .$dc_date. PHP_EOL ."</package>";
	
	
	/* write xml-documents for each (named by DC + metadataId):
	------------------------------------------------------------*/
	$filepath = "DC-XMLS/DC_".$metadataId.".xml";
	write_data_to_file($filepath, $content);
	
	/* clean arrays for next loop:
	------------------------------*/
	unset($identifiers);
	unset($formats);
	unset($titles);
	unset($subjects);
	unset($types);
	unset($descriptions);
	unset($temporals);
	unset($spatials);
	unset($creators);
	unset($contributors);
	unset($publishers);
	unset($languages);
	unset($rights);
	unset($dates);
};

/* write data to file:
=======================*/

function write_data_to_file($filepath, $data) {

	// open file:
	$file = fopen($filepath, 'w');
	
	// write data to file:
	fwrite($file, $data);

	// close file:
	fclose($file);
}

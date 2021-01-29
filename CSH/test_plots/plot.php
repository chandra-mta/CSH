<?php
   $msid_group = $_POST['msid_group'];
   $script = 'script_'.$msid_group;
   $div = 'div_'.$msid_group;
   $dir = "/data/mta4/www/CSH/test_plots/";
   $start = microtime(true);
   usleep(600000);
   while (!is_file($dir.$script)){
	   opendir($dir);
       usleep(200);};
   $time_elapsed = microtime(true) - $start;
   usleep(1000000);
   echo file_get_contents($div);
   echo file_get_contents($script);
   echo "load time: ".$time_elapsed."\n";
   closedir($dir);
/* run python script for test */
?>

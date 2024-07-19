#!/bin/bash

for x in /home/rodur28/novaseq_run2_dimsum-latest/*/
do
	p=${x::-1}
	basename=${p##*/}
	cp $p/$basename'_variant_data_merge.tsv' all_variant_data/$basename'_variant_data_merge.tsv'
	cp $x/report.html all_reports/report_$basename.html
	cp $x/fitness_singles.txt all_fitness/fitness_singles_$basename.txt
	cp $x/fitness_doubles.txt all_fitness/fitness_doubles_$basename.txt
	cp $x/fitness_wildtype.txt all_fitness/fitness_wildtype_$basename.txt
done



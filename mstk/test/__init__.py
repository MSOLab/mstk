""" A sample data set in the standard format


**schedule_metadata.json**

.. note:: 

    Insert 'null' to use a default option

.. code-block:: python

    {
        "schedule_name":[str] <(Required) A name of the schedule: [str]>,
        "file_info": {
            "ac_types_info": [str] <(Optional) A .json file path of AcTypeParam>,
            "activity_info": [str] <(Required) A .csv file path of activity information>,
            "machine_info":  [str] <(Optional) A .csv file path of machine info>,
            "job_info": [str] <(Optional) A .csv file path of job info>
        },
        "horizon": {
            "start": [datetime.datetime] <(Optional) start time of horizon>,
            "end": [datetime.datetime] <(Optional) end time of horizon>
        },
        "plot_option": {
            "legend_on": [bool] <(Required) whether to plot legends>
            "horz_line_on": [bool] <(Required) whether to draw a separating line between machines>
        }
    }


**activity_info.csv**
	
+--------+----------------+----------------+-----------+----------+-----------+-------+
| mc_id  | start          | end            | ac_type   | job_id   | content_1 | ...   |
+========+================+================+===========+==========+===========+=======+
| A1     | 1/1/2020 13:30 | 1/1/2020 17:00 | Operation | Job_21   | value_1   | ...   |
+--------+----------------+----------------+-----------+----------+-----------+-------+


**machine_info.csv**
	
+--------+-----------+-------+
| mc_id  | content_1 | ...   |
+========+===========+=======+
| A1     | value_1   | ...   |
+--------+-----------+-------+


**job_info.csv**
	
+--------+-----------+-------+
| job_id | content_1 | ...   |
+========+===========+=======+
| Job_1  | value_1   | ...   |
+--------+-----------+-------+

"""

import os

current_path = os.path.dirname(os.path.abspath(__file__))

sample_proj_folder = f"{current_path}/sample_proj"

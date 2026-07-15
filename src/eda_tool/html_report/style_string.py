style_string = """<style>
    body {
        font-family: Arial, sans-serif;
        background-color: #f7f7f7;
        margin: 0;
        padding-top: 40px;
    }

    .container {
        margin-left: 10%;
        margin-right: 10%;
    }

    .header {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: white;
        border-bottom: 1px solid #ccc;
        z-index: 100;
        padding: 15px 0;
        display: flex;
        justify-content: flex-end;
    }

    
    .header-content {
        width: 100%;
        max-width: 100%;
        display: flex;
        justify-content: flex-end;
        gap: 20px;
        font-size: 16px;

        padding-right: 20px;
    }

    .dataset-name {
        gap: 16px;
        font-size: 20px;
        width: 100%;
        padding-left: 20px;

    }


    .nav-link {
        text-decoration: none;
        color: #0077cc;
        font-weight: bold;
        font-size: 16px;
    }

    .section {
        margin-top: 40px;
    }

    .section-title {
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    .section-box {


        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }

    .image-box {
        margin-bottom: 20px;
        text-align: center;
    }

    .image-box img {
        max-width: 100%;
        border-radius: 6px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.2);
    }

    .image-caption {
        margin-top: 5px;
        font-size: 14px;
        color: #555;
    }
    /* Tabs container */
    .tabs {
        display: flex;
        gap: 10px;
        border-bottom: 1px solid #ccc;
        margin-bottom: 15px;
    }

    /* Tab buttons */
    .tab-button {
        background: #eee;
        border: none;
        padding: 10px 15px;
        cursor: pointer;
        font-weight: bold;
        border-radius: 6px 6px 0 0;
        color: #555;
    }

    .tab-button.active {
        background: white;
        border-bottom: 2px solid white;
        color: #000;
    }

    /* Tab content */
    

    .tab-content {
        display: block;        
        visibility: hidden;    
        height: 0;             
        overflow: hidden;     
    }

    .tab-content.active {
        visibility: visible;
        height: auto;
        overflow: visible;
    }

    .table-box {
        width: auto;
        border-radius: 6px;
        border: 1px solid #ccc;
        margin-bottom: 20px;
        overflow: hidden; 

    }

    /* width options */
    .table-w1  { flex: 0 0 100%; }
    .table-w2  { flex: 1 1 0; max-width: 50%; }
    .table-w3  { flex: 1 1 0; max-width: 33.333%; }


    .table-box table {
        width: 100%;
        border-collapse: collapse;
    }

    .table-box tr {
        height: 38px;              
    }

    .table-box td {
        padding: 8px 12px;
        vertical-align: middle;
    }

    .table-box .label {
        font-weight: bold;
        width: 80%;
    }

    .table-box .value {
        width: 20%;
        
    }

    .table-box .avalue {
        width: 80%;
    }

    .value-red {
        background: #d9534f;   
        color: white; 
        text-align: center;
        padding: 2px 4px;
        border-radius: 7px;
        display: inline-block;
    }

    .value-blue {
        background: #00A8FF;   
        color: white; 
        text-align: center;
        padding: 2px 4px;
        border-radius: 7px;
        display: inline-block;
    }

    .value-grey {
        background: #2B2B2B;   
        color: white; 
        text-align: center;
        padding: 2px 4px;
        border-radius: 7px;
        display: inline-block;
    }


    /* alternating row colors */
    .table-box tr:nth-child(odd) {
        background: #f2f2f2;
    }

    .table-box tr:nth-child(even) {
        background: #ffffff;
    }

    .table-wrapper {
        display: flex;
        flex-direction: column;
    }

    .table-title {
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 20px; 
    }

    .row-flex {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
    }

    .flex-item {
        display: block;
    }

    .alert-badge {
        display: inline-block;
        min-width: 18px;
        padding: 2px 6px;
        font-size: 12px;
        font-weight: bold;
        color: white;
        background: #d9534f; /* red */
        border-radius: 12px;
        margin-left: 6px;
        line-height: 1;
    }

    /* horizontal scroll */
    

    .scroll-x {
        display: block;
        width: 100%;
        max-width: 100%;
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
    }

    /* index column styling */
    .index-col {
        font-weight: bold;
        background: #f0f0f0;
        width: 60px;
        text-align: center;
        border-right: 1px solid #ccc;
    }

    /* header cells */
    .df-head-table th {
        font-weight: bold;
        background: #f0f0f0;
        padding: 8px 12px;
        border-bottom: 1px solid #ccc;
    }

    /* ensure table cells don't wrap */
    .df-head-table td {
        white-space: nowrap;
    }


    .graph-container {
        width: 100%;
        max-width: 600px;

        /* REMOVE height constraints */
        height: auto;

        /* REMOVE max-height: 400px; */
        /* REMOVE overflow: hidden; */

        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        text-align: center;
    }

    .graph-container img {
        width: auto;
        height: auto;
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }

    .graph-container-third {
        width: 33.333%;          
        max-width: 100%;         
        height: auto;
        max-height: 400px;       
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 0 auto;
        text-align: center;
    }

    .graph-container-third img {
        width: auto;
        height: auto;
        max-width: 100%;         /* shrink proportionally to container width */
        max-height: 100%;        /* shrink proportionally to container height */
        object-fit: contain;     /* never crop, never distort */
    }


    .interactions-tabs,
    .interactions-subtabs {
        display: flex;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }

    .interactions-tab-button,
    .interactions-subtab-button {
        padding: 0.25rem 0.5rem;
        cursor: pointer;
    }

    .interactions-tab-button-active,
    .interactions-subtab-button-active {
        background-color: #ddd;
    }

    .interactions-tab-content,
    .interactions-subtab-content {
        display: none;
    }

    .interactions-tab-content-active,
    .interactions-subtab-content-active {
        display: block;
    }
    #variables .variable-box {
        margin-bottom: 20px;   
    }

    .variable-title {
        font-size: 30px;
    }

    .variable-type {
        font-size: 20px;
        color: grey;
        padding-bottom: 10px;
        padding-top: 10px;
    }


    .details-toggle-row {
        display: flex;
        justify-content: flex-end; /* button goes to the right */
        margin-top: 10px;
        margin-bottom: 10px; /* space before details panel */
    }

    .more-details-btn {
        background: #e0e0e0;
        color: #333;
        padding: 6px 12px;
        border-radius: 4px;
        font-size: 14px;
        cursor: pointer;
        transition: background 0.2s;
    }

    .more-details-btn:hover {
        background: #d0d0d0;
    }


    .details-panel {
        display: none; /* hidden by default */
        margin-top: 15px;
        padding: 15px;
        border: 1px solid #ddd;
        border-radius: 6px;
        background: #fafafa;
    }

    .details-panel.open {
        display: block;
    }

    .details-tabs {
        margin-bottom: 10px;
    }

    .anchor-target {
        scroll-margin-top: 45px; 
    }

    .freq-table {
        width: 100%;
        border-collapse: collapse;
    }

    .freq-table th {
        text-align: left;
        font-weight: bold;
        padding: 6px 8px;
        border-bottom: 1px solid #ccc;
    }

    .freq-table td {
        padding: 6px 8px;
        vertical-align: middle;
    }

    .freq-value {
        width: 60%;
    }

    .freq-count {
        width: 30%;
        text-align: right;
        padding-right: 12px;
    }

    .freq-bar-cell {
        width: 10%;
        position: relative;
    }

    .freq-bar {
        height: 100%;
        background: #4a90e2;
        position: absolute;
        left: 0;
        top: 0;
    }

    .freq-percent-text {
        position: relative;
        z-index: 2;
        font-size: 12px;
        text-align: right;
        padding-right: 4px;
    }

    .inner-tabs {
        display: flex;
        gap: 8px;
        margin-bottom: 8px;
    }

    .inner-tab-button {
        background: #eee;
        border: none;
        padding: 10px 15px;
        cursor: pointer;
        font-weight: bold;
        border-radius: 6px 6px 0 0;
        color: #555;
    }

    .inner-tab-button.active {
        background: white;
        border-bottom: 2px solid white;
        color: #000;
    }

    .inner-tab-content {
        display: none;
    }

    .inner-tab-content.active {
        display: block;
    }



</style>"""
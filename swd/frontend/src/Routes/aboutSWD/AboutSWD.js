/* eslint no-unused-vars:0 */

import React from "react";
import PropTypes from "prop-types";
import { Mobile } from "../../Components/Responsive";
import ExpandableCard from "../../Components/ExpandableCard";
import s from "./AboutSWD.css";
import gql from "graphql-tag";
import { graphql } from "react-apollo";



class AboutSWD extends React.Component {

  render() {
    return (
        
      <Mobile>
        <div className={s.container}>
          <ExpandableCard title="Hostel Facilities">
            <ul class="details">
							<li> Mess selection facility every month. </li>
							<li>Apply for issue of certificate. </li>
							<li> Leave application submission </li>		
						</ul>
            </ExpandableCard>
          <ExpandableCard title="Mess Facilities">
          <ul class="details">
							<li>There are 2 Dinning Halls (A &amp; C) each of capacity 1200. </li>
							<li> Current Caterers: 
								<ul>
									<li>A Dinning Hall : Vinayak Foods</li>
									<li>C Dinning Hall : Aditya cateres </li>
									<li> Mess Rate :   which includes four meals (Breakfast, Lunch, Dinner)</li>
								</ul>
							</li>
						</ul>
            </ExpandableCard>
          <ExpandableCard title = "Financial Aid"/>
          <ExpandableCard title = "Online Services"/>
          </div>
      </Mobile>
      
    );
  }
}


export default AboutSWD;

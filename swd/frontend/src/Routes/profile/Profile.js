/* eslint no-unused-vars:0 */

import React from "react";
import {Mobile} from "../../Components/Responsive";
import s from "./Profile.css";
import {Card, CardMedia, Paper} from "material-ui";
import pic from "./DefaultPic.svg";

class Profile extends React.Component {

    render() {
        const { loading, error, currentUser } = this.props.data;
        if(loading){
            return <p>loading..</p>
        }
        if(error){
            return <p>Some error occured</p>
        } 
        console.log(this.props.data);
        return (
            <Mobile>
                <div className={s.container}>
                    <h2>Profile</h2>
                    <div className={s.profileImg}>
                        <CardMedia>
                            <img src={pic} style={{width: "100%", minWidth: "20%"}} alt="profile_pic"/>
                        </CardMedia>
                    </div>
                    <div className={s.paperDiv}>
                        <Paper zDepth={1} style={{borderRadius: 4, margin: 4, padding: 3}}>

                            <div className={s.infoPaper}>
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>Name</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>John Carter</p>
                                    </div>
                                </div>
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>ID</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>2016AAPS0001G</p>
                                    </div>
                                </div>
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>DOB</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>06/06/1996</p>
                                    </div>
                                </div>
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>Hostel No.</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>AH2</p>
                                    </div>
                                </div>
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>Room No.</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>345</p>
                                    </div>
                                </div>
                                <div className={s.paperElement}>
                                    <div className={s.column1}>
                                        <p><b>CGPA</b></p>
                                    </div>
                                    <div className={s.column2}>
                                        <p>7.409</p>
                                    </div>
                                </div>
                            </div>
                        </Paper>
                    </div>
                    <div className={s.paperDiv}>
                        <Paper zDepth={2} style={{borderRadius: 8, margin: 4, padding: 3}}>
                            <div className={s.infoPaper}>
                                <p><b>Permanent Address</b></p>
                                <p>Plot no. 45, Blacolony, Goa,444444</p>
                            </div>
                        </Paper>
                    </div>
                    <div className={s.paperDiv}>
                        <Paper zDepth={2} style={{borderRadius: 8, margin: 4, padding: 3}}>
                            <div className={s.infoPaper}>
                                <p><b>Contact Details</b></p>
                                <p>123456789</p>
                            </div>

                        </Paper>
                    </div>
                </div>
            </Mobile>

        );
    }
}


export default Profile;

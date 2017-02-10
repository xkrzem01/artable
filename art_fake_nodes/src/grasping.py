#!/usr/bin/env python

import rospy
from actionlib import SimpleActionServer
from art_msgs.msg import pickplaceAction, pickplaceGoal, pickplaceResult, pickplaceFeedback
import time
import random


class FakeGrasping:
    ALWAYS = 0
    NEVER = 1
    RANDOM = 2

    def __init__(self):
        self.server = SimpleActionServer('/art/pr2/left_arm/pp', pickplaceAction,
                                         execute_cb=self.pickplace_cb)
        self.objects = self.ALWAYS
        self.grasp = self.ALWAYS
        self.place = self.ALWAYS
        self.object_randomness = 0.8  # 80% of time object is known
        self.grasp_randomness = 0.4
        self.place_randomness = 0.4
        random.seed()

    def pickplace_cb(self, goal):
        result = pickplaceResult()
        feedback = pickplaceFeedback()
        if not (goal.operation == pickplaceGoal.PICK or
                goal.operation == pickplaceGoal.PLACE or
                goal.operation == pickplaceGoal.PICK_AND_PLACE):
            result.result = pickplaceResult.BAD_REQUEST
            rospy.logerr("BAD_REQUEST, Unknown operation")
            self.server.set_aborted(result, "Unknown operation")
            return

        if self.objects == self.ALWAYS:
            pass
        elif self.objects == self.NEVER:
            result.result = pickplaceResult.BAD_REQUEST
            rospy.logerr("BAD_REQUEST, Unknown object id")
            self.server.set_aborted(result, "Unknown object id")
            return
        elif self.objects == self.RANDOM:
            nmbr = random.random()
            if nmbr > self.object_randomness:
                result.result = pickplaceResult.BAD_REQUEST
                rospy.logerr("BAD_REQUEST, Unknown object id")
                self.server.set_aborted(result, "Unknown object id")
                return

        grasped = False

        if goal.operation == pickplaceGoal.PICK or goal.operation == pickplaceGoal.PICK_AND_PLACE:
            if self.grasp == self.ALWAYS:
                grasped = True
                pass
            elif self.grasp == self.NEVER:
                result.result = pickplaceResult.FAILURE
                rospy.logerr("FAILURE, Pick Failed")
                self.server.set_aborted(result, "Pick Failed")
                return

            tries = 5
            max_attempts = 5
            while tries > 0:
                feedback.attempt = (max_attempts - tries) + 1
                tries -= 1
                self.server.publish_feedback(feedback)

                if self.grasp == self.RANDOM:
                    nmbr = random.random()
                    if nmbr < self.grasp_randomness:
                        grasped = True
                if grasped:
                    break

            if self.server.is_preempt_requested():
                self.server.set_preempted(result, "Pick canceled")
                rospy.logerr("Preempted")
                return

            if not grasped:
                result.result = pickplaceResult.FAILURE
                self.server.set_aborted(result, "Pick failed")
                rospy.logerr("FAILURE, Pick Failed")
                return
        placed = False
        if goal.operation == pickplaceGoal.PICK_AND_PLACE or goal.operation == pickplaceGoal.PLACE:
            if self.place == self.ALWAYS:
                placed = True
                pass
            elif self.place == self.NEVER:
                result.result = pickplaceResult.FAILURE
                self.server.set_aborted(result, "Place Failed")
                rospy.logerr("FAILURE, Place Failed")
                return

            tries = 5
            max_attempts = 5
            while tries > 0:
                feedback.attempt = (max_attempts - tries) + 1
                tries -= 1
                self.server.publish_feedback(feedback)

                if self.place == self.RANDOM:
                    nmbr = random.random()
                    if nmbr < self.place_randomness:
                        placed = True
                if placed:
                    break
            if not placed:
                result.result = pickplaceResult.FAILURE
                self.server.set_aborted(result, "Place failed")
                rospy.logerr("FAILURE, Place Failed")
                return

        result.result = pickplaceResult.SUCCESS
        self.server.set_succeeded(result)
        rospy.loginfo("SUCCESS")
        print("Finished")


if __name__ == '__main__':
    rospy.init_node('fake_grasping')
    ''',log_level=rospy.DEBUG'''

    try:
        node = FakeGrasping()

        rospy.spin()
    except rospy.ROSInterruptException:
        pass

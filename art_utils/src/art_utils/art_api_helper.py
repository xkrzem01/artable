#!/usr/bin/env python

import rospy
from art_msgs.srv import getProgram, storeProgram, ProgramIdTrigger, getObjectType, getProgramHeaders, storeObjectType

# TODO make brain version a new class (based on ArtApiHelper)


class ArtApiHelper(object):

    def __init__(self, brain=False):

        # DB API
        self.get_prog_srv = rospy.ServiceProxy('/art/db/program/get', getProgram)
        self.store_prog_srv = rospy.ServiceProxy('/art/db/program/store', storeProgram)
        self.delete_prog_srv = rospy.ServiceProxy('/art/db/program/delete', ProgramIdTrigger)
        self.prog_ro_set_srv = rospy.ServiceProxy('/art/db/program/readonly/set', ProgramIdTrigger)
        self.prog_ro_clear_srv = rospy.ServiceProxy('/art/db/program/readonly/clear', ProgramIdTrigger)
        self.get_program_headers_srv = rospy.ServiceProxy('/art/db/program_headers/get', getProgramHeaders)
        self.get_obj_type_srv = rospy.ServiceProxy('/art/db/object_type/get', getObjectType)
        self.store_obj_type_srv = rospy.ServiceProxy('/art/db/object_type/store', storeObjectType)

        # Brain API
        self.brain = brain
        if not self.brain:
            self.start_program_srv = rospy.ServiceProxy('/art/brain/program/start', ProgramIdTrigger)

        self._object_type_cache = {}

    def wait_for_api(self):

        self.get_prog_srv.wait_for_service()
        self.store_prog_srv.wait_for_service()
        self.get_program_headers_srv.wait_for_service()
        self.get_obj_type_srv.wait_for_service()
        self.store_obj_type_srv.wait_for_service()

        if not self.brain:
            self.start_program_srv.wait_for_service()

    def load_program(self, prog_id):

        rospy.loginfo('Loading program: ' + str(prog_id))

        try:
            resp = self.get_prog_srv(prog_id)
        except rospy.ServiceException as e:
            print "Service call failed: %s" % e
            return None

        if not resp.success:
            return None
        else:
            return resp.program

    def get_program_headers(self, ids=[]):

        try:
            resp = self.get_program_headers_srv(ids)
        except rospy.ServiceException as e:
            print "Service call failed: %s" % e
            return None

        return resp.headers

    def store_program(self, prog):

        try:
            resp = self.store_prog_srv(prog)
        except rospy.ServiceException as e:
            print "Service call failed: %s" % e
            return False

        return resp.success

    def delete_program(self, prog_id):

        try:
            resp = self.delete_prog_srv(prog_id)
        except rospy.ServiceException as e:
            print "Service call failed: %s" % e
            return False, ""

        return resp.success, resp.error

    def program_set_ro(self, prog_id):

        try:
            resp = self.prog_ro_set_srv(prog_id)
        except rospy.ServiceException as e:
            print "Service call failed: %s" % e
            return False, ""

        return resp.success, resp.error

    def program_clear_ro(self, prog_id):

        try:
            resp = self.prog_ro_clear_srv(prog_id)
        except rospy.ServiceException as e:
            print "Service call failed: %s" % e
            return False, ""

        return resp.success, resp.error

    def start_program(self, prog_id):

        try:
            resp = self.start_program_srv(prog_id)
        except rospy.ServiceException as e:
            print "Service call failed: %s" % e
            return (False, "")

        return resp.success, resp.error

    def get_object_type(self, name):

        if name not in self._object_type_cache:

            try:
                resp = self.get_obj_type_srv(name)
            except rospy.ServiceException as e:
                print "Service call failed: %s" % e
                return None

            if not resp.success:
                return None
            else:
                self._object_type_cache[name] = resp.object_type

        return self._object_type_cache[name]

    def store_object_type(self, ot):

        try:
            resp = self.store_obj_type_srv(ot)
        except rospy.ServiceException as e:
            print "Service call failed: " + str(e)
            return False

        return resp.success

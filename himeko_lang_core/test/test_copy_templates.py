from himeko.hbcm.elements.edge import HyperEdge
from himeko.hbcm.elements.vertex import HyperVertex
from himeko.transformations.text.generate_text import TextGenerator
from himeko_lang.processing.parse_description import ParseDescriptionEdgeFromFile, ParseDescriptionEdge
from .test_ancestor_testcase import TestAncestorTestCase

class TestAstParsingWithReferences(TestAncestorTestCase):

    def test_copy_templates(self):
        e = ParseDescriptionEdgeFromFile("parse_edge", 0, 0, b'0', b'0', "label", None)
        p = "examples/kinematics/chicken_kinematics.himeko"
        library_path = "examples/kinematics/"
        h = e.execute(path=p, library_path=library_path)
        root = h[-1]
        self.assertEqual(root.name, "root")
        self.assertIsNotNone(root["right_leg"])
        self.assertIsNotNone(root["left_leg"])
        self.assertIsNotNone(root["right_wing"])
        self.assertIsNotNone(root["left_wing"])
        # Assert new instances are different
        self.assertNotEqual(root["right_leg"], root["left_leg"])
        self.assertNotEqual(root["right_leg"]["right_leg_femur"], root["left_leg"]["left_leg_femur"])
        self.assertEqual(root["right_leg"]["right_leg_femur"].name, "right_leg_femur")
        self.assertEqual(root["left_leg"]["left_leg_femur"].name, "left_leg_femur")
        # Assert new instance has the template as stereotype
        self.assertIn("femur", root["left_leg"]["left_leg_femur"].stereotype.nameset)
        self.assertIn("bone", root["left_leg"]["left_leg_femur"].stereotype.nameset)
        # Check for the right leg
        self.assertEqual(root["right_leg"]["right_leg_femur"].name, "right_leg_femur")
        self.assertEqual(root["right_leg"]["right_leg_tibia"].name, "right_leg_tibia")
        self.assertEqual(root["right_leg"]["right_leg_tarsus"].name, "right_leg_tarsus")
        # Check stereotype
        self.assertIn("tarsus", root["right_leg"]["right_leg_tarsus"].stereotype.nameset)
        # Check edge tarso-metatarsal
        self.assertEqual(root["right_leg"]["right_leg_tarsometatarsus"].name, "right_leg_tarsometatarsus")
        self.assertEqual(root["right_leg"]["right_leg_tarsometatarsus"].stereotype.nameset, {"tarsometatarsus", "joint"})
        self.assertEqual(root["right_leg"]["right_leg_tarsometatarsus"].get_parent().name, "right_leg")
        # Check edge relations
        self.assertEqual(list(root["right_leg"]["right_leg_tarsometatarsus"].out_relations())[0].value, 1.0)
        self.assertEqual(list(root["right_leg"]["right_leg_tarsometatarsus"].out_relations())[0].target.name, "right_leg_tarsus")
        self.assertEqual(list(root["right_leg"]["right_leg_tarsometatarsus"].in_relations())[0].value, 1.0)
        self.assertEqual(list(root["right_leg"]["right_leg_tarsometatarsus"].in_relations())[0].target.name, "right_leg_metatarsus")
        self.assertIn("metatarsus",
            list(root["right_leg"]["right_leg_tarsometatarsus"].in_relations())[0].target.stereotype.nameset)
        # Check other tarso-metatarsal edge
        self.assertEqual(list(root["left_leg"]["left_leg_tarsometatarsus"].out_relations())[0].value, 1.0)
        self.assertEqual(list(root["left_leg"]["left_leg_tarsometatarsus"].out_relations())[0].target.name, "left_leg_tarsus")
        self.assertEqual(list(root["left_leg"]["left_leg_tarsometatarsus"].in_relations())[0].value, 1.0)
        self.assertEqual(list(root["left_leg"]["left_leg_tarsometatarsus"].in_relations())[0].target.name, "left_leg_metatarsus")
        self.assertIn("metatarsus",
                      list(root["right_leg"]["right_leg_tarsometatarsus"].in_relations())[0].target.stereotype.nameset)
        # Get numbers
        self.assertIsInstance(root["right_leg"], HyperVertex)
        right_leg: HyperVertex = root["right_leg"]
        # Check for the right wing
        self.assertEqual(root["right_wing"]["right_wing_coracoid"].name, "right_wing_coracoid")
        # Check a joint stereotype
        self.assertIn("joint", root["right_wing"]["right_wing_coracoid_humerus"].stereotype.nameset)
        # Check that the joint stereotype is a hyperedge
        self.assertIsInstance(root["right_wing"]["right_wing_coracoid_humerus"], HyperEdge)
        self.assertIsInstance(list(root["right_wing"]["right_wing_coracoid_humerus"].stereotype)[-1], HyperEdge)
        # Changing values (copies)
        root["epistropheus"]["position"].value[0] = 5.0
        self.assertNotEqual( h[0]["state"]["position"], h[0]["elements"]["bone"]["position"])
        self.assertNotEqual(root["epistropheus"]["position"], root["sternum"]["position"])
        self.assertNotEqual(root["epistropheus"]["position"].value, root["sternum"]["position"].value)
        self.assertEqual(root["epistropheus"]["position"].value[0], 5.0)
        self.assertEqual(root["sternum"]["position"].value[0], 0.0)
        self.assertEqual(root["epistropheus"]["position"].value, [5.0, 0.0, 0.0])
        self.assertEqual(root["sternum"]["position"].value, [0.0, 0.0, 0.0])
        root["left_wing"]["left_wing_coracoid"]["position"].value[0] = 5.0

        self.assertEqual(root["left_wing"]["left_wing_coracoid"]["position"].value, [5.0, 0.0, 0.0])
        self.assertEqual(root["right_wing"]["right_wing_coracoid"]["position"].value, [0.0, 0.0, 0.0])

        self.assertNotEqual(root["left_wing"]["left_wing_coracoid"], root["right_wing"]["right_wing_coracoid"])

    def test_reparse_text(self):
        e = ParseDescriptionEdgeFromFile("parse_edge", 0, 0, b'0', b'0', "label", None)
        p = "examples/kinematics/chicken_kinematics.himeko"
        library_path = "examples/kinematics/"
        h = e.execute(path=p, library_path=library_path)
        root = h[-1]
        self.assertEqual(root.name, "root")
        h_text = ParseDescriptionEdge(
            "parse_edge", 0, 0, b'0', b'0', "label", None)
        h_text_generator = TextGenerator(
            "text_generator", 0, 0, b'0', b'0', "label", None)
        h_reparsed = h_text.execute(text=h_text_generator(root), library_path=library_path)
        root_reparsed = h_reparsed[-1]
        self.assertEqual(root_reparsed.name, "root")
        # Check
        self.assertIsNotNone(root["right_leg"])
        self.assertIsNotNone(root["left_leg"])
        self.assertIsNotNone(root["right_wing"])
        self.assertIsNotNone(root["left_wing"])
        # Assert new instances are different
        self.assertNotEqual(root["right_leg"], root["left_leg"])
        self.assertNotEqual(root["right_leg"]["right_leg_femur"], root["left_leg"]["left_leg_femur"])
        self.assertEqual(root["right_leg"]["right_leg_femur"].name, "right_leg_femur")
        self.assertEqual(root["left_leg"]["left_leg_femur"].name, "left_leg_femur")
        # Assert new instance has the template as stereotype
        self.assertIn("femur", root["left_leg"]["left_leg_femur"].stereotype.nameset)
        self.assertIn("bone", root["left_leg"]["left_leg_femur"].stereotype.nameset)
        # Check for the right leg
        self.assertEqual(root["right_leg"]["right_leg_femur"].name, "right_leg_femur")
        self.assertEqual(root["right_leg"]["right_leg_tibia"].name, "right_leg_tibia")
        self.assertEqual(root["right_leg"]["right_leg_tarsus"].name, "right_leg_tarsus")
        # Check stereotype
        self.assertIn("tarsus", root["right_leg"]["right_leg_tarsus"].stereotype.nameset)
